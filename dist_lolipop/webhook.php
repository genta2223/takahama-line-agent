<?php
/**
 * LINE Messaging API Webhook Relay to Google Apps Script (GAS)
 * 
 * LINE Developers enforces HTTP 200 responses directly and does not follow
 * 302 redirects from Google Apps Script Web Apps.
 * This proxy script accepts LINE Webhook POST, follows redirects to GAS,
 * and always returns HTTP 200 OK to the LINE platform.
 */

// Target Google Apps Script Web App URL
define('GAS_WEBHOOK_URL', 'https://script.google.com/macros/s/AKfycbxRH-6fQfevgFSVPwVC-jhs2VG6q6eLf76EAIkAC1_6GQNArTJ4Gzp_IVjJcqrdMtub/exec');

// Respond to GET or verification checks immediately
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(200);
    echo "OK - LINE Webhook Relay is Running";
    exit;
}

// Read raw JSON body from LINE platform
$rawBody = file_get_contents('php://input');

if (empty($rawBody)) {
    http_response_code(200);
    echo "OK";
    exit;
}

// Initialize cURL to forward payload to GAS
$ch = curl_init();

curl_setopt_array($ch, [
    CURLOPT_URL => GAS_WEBHOOK_URL,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $rawBody,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json; charset=UTF-8',
        'Content-Length: ' . strlen($rawBody)
    ],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_FOLLOWLOCATION => true, // Essential for GAS 302 redirect
    CURLOPT_MAXREDIRS => 5,
    CURLOPT_TIMEOUT => 25,
    CURLOPT_SSL_VERIFYPEER => true
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlErr = curl_error($ch);
curl_close($ch);

// Always respond HTTP 200 to LINE to prevent webhook delivery retries
http_response_code(200);
echo "OK";
