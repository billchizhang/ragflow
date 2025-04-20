/**
 * Email Utility Module
 * 
 * This module provides email functionality for the application,
 * specifically for sending password reset emails with verification PINs.
 * 
 * It utilizes Nodemailer to configure and send emails through the
 * email service defined in environment variables.
 */

import nodemailer from 'nodemailer';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Nodemailer Transporter
 * 
 * Configures the email transport mechanism using environment variables:
 * - EMAIL_SERVICE: The email service provider (e.g., 'gmail', 'outlook')
 * - EMAIL_USER: The sender's email address
 * - EMAIL_PASSWORD: The sender's email password or app-specific password
 * 
 * For Gmail, you typically need to use an app-specific password
 * rather than your account password due to security restrictions.
 */
const transporter = nodemailer.createTransport({
  service: process.env.EMAIL_SERVICE,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASSWORD
  }
});

/**
 * Send Password Reset Email
 * 
 * Sends an email containing a 6-digit PIN for password reset verification.
 * The email includes instructions and formatting for a professional appearance.
 * 
 * @param {string} to - Recipient's email address
 * @param {string} pin - 6-digit PIN for password reset verification
 * @returns {Promise<object>} - Resolves with Nodemailer info object on success
 * @throws {Error} - Throws if email sending fails
 */
export async function sendPasswordResetEmail(to, pin) {
  // Define email content and options
  const mailOptions = {
    from: process.env.EMAIL_FROM, // Sender address from environment variables
    to, // Recipient address
    subject: 'Asireon AI - Password Reset',
    // HTML email body with styling for better presentation
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4A5568;">Password Reset Request</h2>
        <p>We received a request to reset your password for your Asireon AI account.</p>
        <p>Your password reset PIN is:</p>
        <div style="background-color: #EDF2F7; padding: 12px; font-size: 24px; font-weight: bold; letter-spacing: 2px; text-align: center; margin: 16px 0;">
          ${pin}
        </div>
        <p>This PIN will expire in 15 minutes.</p>
        <p>If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
        <p style="margin-top: 24px;">Regards,<br>The Asireon AI Team</p>
      </div>
    `
  };

  try {
    // Attempt to send the email using the configured transporter
    const info = await transporter.sendMail(mailOptions);
    // Log success information
    console.log('Email sent: %s', info.messageId);
    return info;
  } catch (error) {
    // Log detailed error information for debugging
    console.error('Error sending email:', error);
    // Re-throw the error for handling by the calling function
    throw error;
  }
}

/**
 * Send Subscription Confirmation Email
 * 
 * Sends an email confirming subscription purchase with authorization code.
 * 
 * @param {string} to - Recipient's email address
 * @param {Object} subscriptionData - Subscription information
 * @param {string} subscriptionData.authCode - Authorization code
 * @param {string} subscriptionData.tierName - Subscription tier name
 * @param {string} subscriptionData.expiryDate - Subscription expiry date
 * @returns {Promise<object>} - Resolves with Nodemailer info object on success
 * @throws {Error} - Throws if email sending fails
 */
export async function sendSubscriptionEmail(to, subscriptionData) {
  const { authCode, tierName, expiryDate } = subscriptionData;
  
  // Define email content and options
  const mailOptions = {
    from: process.env.EMAIL_FROM, // Sender address from environment variables
    to, // Recipient address
    subject: `Asireon AI - Your ${tierName} Subscription`,
    // HTML email body with styling for better presentation
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4A5568;">Thank You for Your Purchase!</h2>
        <p>Thank you for subscribing to Asireon AI's ${tierName} plan.</p>
        <p>Your authorization code is:</p>
        <div style="background-color: #EDF2F7; padding: 12px; font-size: 18px; font-weight: bold; letter-spacing: 1px; text-align: center; margin: 16px 0; font-family: monospace;">
          ${authCode}
        </div>
        <p>Please use this code during registration to activate your ${tierName} subscription.</p>
        <p>This code will expire on ${expiryDate}.</p>
        <p>To register:</p>
        <ol>
          <li>Go to <a href="https://app.asireon.ai/register">app.asireon.ai/register</a></li>
          <li>Fill in your information</li>
          <li>Enter the authorization code when prompted</li>
        </ol>
        <p style="margin-top: 24px;">Regards,<br>The Asireon AI Team</p>
      </div>
    `
  };

  try {
    // Attempt to send the email using the configured transporter
    const info = await transporter.sendMail(mailOptions);
    // Log success information
    console.log('Email sent: %s', info.messageId);
    return info;
  } catch (error) {
    // Log detailed error information for debugging
    console.error('Error sending email:', error);
    // Re-throw the error for handling by the calling function
    throw error;
  }
} 