// notify.js — Branded Gemini CLI Task Completion Notifier
const nodemailer = require('nodemailer');

const SENDER     = 'abhay315204@gmail.com';
const RECEIVER   = 'abhay31204@gmail.com'; // Using the receiver address provided
const APP_PASS   = 'sooo kysh pphn lgdt';
const AGENT_NAME = 'Gemini CLI';
const BRAND_COLOR= '#1B72E8';
const LOGO_URL   = 'https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg';
const TIMESTAMP  = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });

const taskSummary = `
<ul style="padding-left: 20px; color: rgba(235,235,235,0.7); font-size: 14px;">
  <li style="margin-bottom: 8px;"><strong>📄 PDF Export System:</strong> Integrated xhtml2pdf with a custom clinical letterhead and one-click download functionality.</li>
  <li style="margin-bottom: 8px;"><strong>🔍 Smart Remedy Integration:</strong> Built an autocomplete search API connected to Allen's Keynotes database for instant prescription suggestions.</li>
  <li style="margin-bottom: 8px;"><strong>📊 Practice Analytics:</strong> Created a visual dashboard breakdown of 14-day case volume, patient sex distribution, and age demographics.</li>
  <li style="margin-bottom: 8px;"><strong>🏗️ Design Overhaul:</strong> Finalized the "Paper & Ink" premium UI across all case paper management pages.</li>
</ul>
`;

const htmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Task Complete</title>
</head>
<body style="margin:0;padding:0;background-color:#0D0D0D;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0D0D0D;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0" style="background:#141414;border:0.5px solid rgba(255,255,255,0.08);max-width:580px;width:100%;">

          <!-- Header with agent branding -->
          <tr>
            <td style="background:${BRAND_COLOR};padding:32px 40px;text-align:left;">
              <img src="${LOGO_URL}" width="36" height="36" alt="${AGENT_NAME}" 
                   style="vertical-align:middle;margin-right:12px;border-radius:6px;" />
              <span style="color:#ffffff;font-size:13px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;vertical-align:middle;">
                ${AGENT_NAME}
              </span>
            </td>
          </tr>

          <!-- Main content -->
          <tr>
            <td style="padding:48px 40px 32px;">
              <p style="margin:0 0 8px;color:rgba(255,255,255,0.4);font-size:11px;letter-spacing:0.15em;text-transform:uppercase;font-family:monospace;">
                Project Status
              </p>
              <h1 style="margin:0 0 24px;color:#EBEBEB;font-size:32px;font-weight:700;line-height:1.1;letter-spacing:-0.02em;">
                Advanced Features<br/>Implemented ✓
              </h1>
              
              <div style="margin:0 0 32px; color:rgba(235,235,235,0.6); font-size:15px; line-height:1.65;">
                Hello Abhay, the final phases of the HomeoCompare Case Paper system are now complete. Here is the implementation detail:
                <br/><br/>
                ${taskSummary}
              </div>

              <!-- Divider -->
              <div style="height:0.5px;background:rgba(255,255,255,0.08);margin-bottom:32px;"></div>

              <!-- Meta info -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding-bottom:16px;">
                    <span style="color:rgba(255,255,255,0.35);font-size:11px;font-family:monospace;letter-spacing:0.1em;text-transform:uppercase;">Agent</span><br/>
                    <span style="color:#EBEBEB;font-size:14px;font-family:monospace;margin-top:4px;display:inline-block;">${AGENT_NAME}</span>
                  </td>
                  <td style="padding-bottom:16px;">
                    <span style="color:rgba(255,255,255,0.35);font-size:11px;font-family:monospace;letter-spacing:0.1em;text-transform:uppercase;">Completed At</span><br/>
                    <span style="color:#EBEBEB;font-size:14px;font-family:monospace;margin-top:4px;display:inline-block;">${TIMESTAMP}</span>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <div style="height:0.5px;background:rgba(255,255,255,0.08);margin:16px 0 32px;"></div>

              <p style="margin:0;color:rgba(235,235,235,0.35);font-size:12px;line-height:1.6;">
                This is an automated notification sent by your local agent workflow.<br/>
                The PDF Export, Remedy Search, and Practice Analytics are now fully verified.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:0.5px solid rgba(255,255,255,0.06);">
              <p style="margin:0;color:rgba(255,255,255,0.2);font-size:11px;font-family:monospace;letter-spacing:0.08em;">
                SENT VIA NOTIFY.JS — ${AGENT_NAME} WORKFLOW
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
`;

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: SENDER,
    pass: APP_PASS,
  },
});

transporter.sendMail({
  from: `"${AGENT_NAME} Notifier" <${SENDER}>`,
  to: RECEIVER,
  subject: `✅ ${AGENT_NAME} — Advanced Features Complete`,
  html: htmlTemplate,
}, (err, info) => {
  if (err) {
    console.error('❌ Failed to send email:', err.message);
    process.exit(1);
  }
  console.log(`✅ Branded notification sent to ${RECEIVER}`);
  console.log(`   Message ID: ${info.messageId}`);
});
