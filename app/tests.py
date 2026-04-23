from django.test import TestCase, Client
from django.urls import reverse
from .models import CasePaperUser, CasePaper
from django.utils import timezone
from datetime import timedelta

class CasePaperSettingsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CasePaperUser.objects.create(
            username="testuser",
            email="test@example.com",
            physician_name="Dr. Test",
            specialization="Homeopathy",
            clinic_name="Test Clinic",
            contact_number="1234567890",
            address="Test Address"
        )
        # Mock login by setting session variable
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

    def test_settings_get(self):
        """Test that settings page loads correctly with user data"""
        response = self.client.get(reverse('case_paper_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'case_paper/settings.html')
        self.assertEqual(response.context['user'].physician_name, "Dr. Test")
        self.assertEqual(response.context['total_cases'], 0)

    def test_settings_post_save(self):
        """Test that settings are saved correctly on POST"""
        post_data = {
            'physician_name': 'Dr. Updated',
            'specialization': 'Updated Specialization',
            'clinic_name': 'Updated Clinic',
            'contact_number': '0987654321',
            'email': 'updated@example.com',
            'address': 'Updated Address'
        }
        response = self.client.post(reverse('case_paper_settings'), post_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['settings_saved'])
        
        # Refresh user from DB
        self.user.refresh_from_db()
        self.assertEqual(self.user.physician_name, "Dr. Updated")
        self.assertEqual(self.user.specialization, "Updated Specialization")
        self.assertEqual(self.user.clinic_name, "Updated Clinic")
        self.assertEqual(self.user.contact_number, "0987654321")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.address, "Updated Address")

    def test_settings_case_counts(self):
        """Test that case counts are correct in context"""
        CasePaper.objects.create(user=self.user, status='draft', case_id='HC-20260419-0001')
        CasePaper.objects.create(user=self.user, status='complete', case_id='HC-20260419-0002')
        
        response = self.client.get(reverse('case_paper_settings'))
        self.assertEqual(response.context['total_cases'], 2)
        self.assertEqual(response.context['draft_cases'], 1)
        self.assertEqual(response.context['completed_cases'], 1)

class CasePaperDashboardFilterTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CasePaperUser.objects.create(username="testuser", email="test@example.com")
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()
        
        # Create cases with different dates and statuses
        now = timezone.now()
        CasePaper.objects.create(
            user=self.user, 
            status='draft', 
            case_id='HC-DRAFT-1',
            preliminary={'patient_name': 'Alice'}
        )
        # Manually update created_at for date testing (auto_now_add makes it hard to set directly in create)
        c2 = CasePaper.objects.create(
            user=self.user, 
            status='complete', 
            case_id='HC-COMP-1',
            preliminary={'patient_name': 'Bob'}
        )
        CasePaper.objects.filter(id=c2.id).update(created_at=now - timedelta(days=5))

    def test_dashboard_filter_search(self):
        response = self.client.get(reverse('case_paper_dashboard'), {'search': 'Alice'})
        self.assertEqual(len(response.context['cases']), 1)
        self.assertEqual(response.context['cases'][0].case_id, 'HC-DRAFT-1')

    def test_dashboard_filter_status(self):
        response = self.client.get(reverse('case_paper_dashboard'), {'status': 'complete'})
        self.assertEqual(len(response.context['cases']), 1)
        self.assertEqual(response.context['cases'][0].status, 'complete')

    def test_dashboard_filter_date(self):
        five_days_ago = (timezone.now() - timedelta(days=5)).date().isoformat()
        response = self.client.get(reverse('case_paper_dashboard'), {'date_from': five_days_ago, 'date_to': five_days_ago})
        # Note: Depending on implementation details (created_at__date), Bob should match
        self.assertEqual(len(response.context['cases']), 1)
        self.assertEqual(response.context['cases'][0].preliminary['patient_name'], 'Bob')

    def test_edit_page_load(self):
        """Test that the edit page loads without 500 error"""
        case = CasePaper.objects.create(
            user=self.user, 
            case_id='HC-EDIT-TEST',
            preliminary={'patient_name': 'Edit Test', 'consultation_date': '2026-04-19'}
        )
        response = self.client.get(reverse('case_paper_edit', args=[case.case_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'case_paper/form.html')
        self.assertEqual(response.context['case'].case_id, 'HC-EDIT-TEST')

    def test_case_delete_form(self):
        """Test deleting a case via form POST"""
        case = CasePaper.objects.create(user=self.user, case_id='HC-DEL-TEST')
        response = self.client.post(reverse('case_paper_delete'), {'case_id': case.case_id})
        self.assertEqual(response.status_code, 302) # Redirect to dashboard
        self.assertFalse(CasePaper.objects.filter(case_id='HC-DEL-TEST').exists())
