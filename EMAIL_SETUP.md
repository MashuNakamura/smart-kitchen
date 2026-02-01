# Email Configuration Guide for OTP System

## Overview
The OTP (One-Time Password) system now supports email delivery using Gmail's SMTP server. When properly configured, users will receive their OTP codes via email instead of viewing them in the console.

## Gmail Setup Instructions

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com
2. Navigate to **Security** → **2-Step Verification**
3. Follow the steps to enable 2-factor authentication if not already enabled

### Step 2: Generate App Password
1. Visit: https://myaccount.google.com/apppasswords
2. Select **App**: Choose "Mail"
3. Select **Device**: Choose "Other" and enter "SmartKitchen"
4. Click **Generate**
5. Google will display a 16-character password (e.g., `abcd efgh ijkl mnop`)
6. **Important**: Copy this password immediately - you won't be able to see it again!

### Step 3: Configure Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your email configuration:
   ```bash
   # Email Configuration (Gmail SMTP)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # Your 16-character app password
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

3. **Do NOT commit the `.env` file** - it's already in `.gitignore`

## How It Works

### Development Mode (No Email Configured)
- OTP is logged to console
- OTP is included in API response
- Message: "OTP generated. Check server logs for code."

### Production Mode (Email Configured)
- OTP is sent via email
- OTP is NOT included in API response (unless `FLASK_ENV=development`)
- Message: "OTP sent successfully. Please check your email."

### Email Template
Users receive a professional HTML email containing:
- SmartKitchen branding
- Large, centered OTP code
- Expiration notice (10 minutes)
- Security notice if they didn't register

## Testing Email Configuration

### Test 1: Check SMTP Connection
```python
import os
os.environ['SMTP_USERNAME'] = 'your-email@gmail.com'
os.environ['SMTP_PASSWORD'] = 'your-app-password'

import utils
result = utils.send_otp_email('test@example.com', '123456')
print(f'Email sent: {result}')
```

### Test 2: Full Registration Flow
1. Start the server: `python app.py`
2. Request OTP: 
   ```bash
   curl -X POST http://localhost:5000/api/request-otp \
     -H "Content-Type: application/json" \
     -d '{"email": "your-email@gmail.com"}'
   ```
3. Check your email inbox for the OTP code
4. Complete registration with the OTP

## Troubleshooting

### Error: "SMTP credentials not configured"
- **Cause**: `SMTP_USERNAME` or `SMTP_PASSWORD` not set in `.env`
- **Solution**: Follow Step 3 above to configure email settings

### Error: "Authentication failed"
- **Cause**: Wrong password or app password not generated
- **Solution**: 
  - Make sure you're using the **app password**, not your regular Google password
  - Re-generate a new app password if needed

### Error: "Connection refused" or "Connection timed out"
- **Cause**: Network/firewall blocking SMTP port
- **Solution**: 
  - Check if port 587 is open
  - Try using port 465 with SSL instead

### Email not received
- Check spam/junk folder
- Verify email address is correct
- Check server logs for error messages
- Try sending a test email using the test script above

## Alternative Email Providers

If you prefer not to use Gmail, you can configure other SMTP providers:

### SendGrid
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### AWS SES
```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

## Security Best Practices

1. ✅ **Never commit `.env` file** - already in `.gitignore`
2. ✅ **Use app passwords** - not your main Google password
3. ✅ **Keep credentials secret** - don't share or expose them
4. ✅ **Rotate passwords periodically** - generate new app passwords regularly
5. ✅ **Use different emails** - consider using a dedicated email for app notifications

## Production Deployment

When deploying to production:

1. Set environment variables on your server (not in `.env` file)
2. Set `FLASK_ENV=production` and `DEBUG=false`
3. Ensure SMTP credentials are properly configured
4. Test email sending before going live
5. Monitor email delivery logs

## Rate Limiting

The OTP request endpoint is rate-limited to prevent abuse:
- **3 requests per minute** per IP address
- This helps prevent spam and protects your email quota

## Support

If you encounter issues:
1. Check server logs for detailed error messages
2. Verify your `.env` configuration
3. Test with the provided test scripts
4. Check Gmail security settings
