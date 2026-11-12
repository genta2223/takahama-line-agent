<?php
/**
 * LINE Messaging API Webhook Relay to Google Apps Script (GAS)
 * Asynchronous response version:
 * 1. Read input payload
 * 2. Immediately flush HTTP 200 OK to LINE Platform
 * 3. Forward payload to GAS in background with 302 redirect tracking
 */

// Target Google Apps Script Web App URL
define('GAS_WEBHOOK_URL', 'https://script.google.com/macros/s/AKfycbxRH-6fQfevgFSVPwVC-jhs2VG6q6eLf76EAIkAC1_6GQNArTJ4Gzp_IVjJcqrdMtub/exec');

// Read raw body from LINE platform
$rawBody = file_get_contents('php://input');

// Handle non-POST or empty payload immediately
if ($_SERVER['REQUEST_METHOD'] !== 'POST' || empty($rawBody)) {
    http_response_code(200);
    header('Content-Type: text/plain; charset=UTF-8');
    echo "OK";
    exit;
}

// -------------------------------------------------------------
// 1. Immediately return HTTP 200 OK and close connection to LINE
// -------------------------------------------------------------
ignore_user_abort(true);
set_time_limit(35);

ob_start();
http_response_code(200);
header('Content-Type: text/plain; charset=UTF-8');
echo 'OK';
$size = ob_get_length();
header("Content-Length: $size");
header('Connection: close');
ob_end_flush();
@ob_flush();
flush();

if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request();
}

// -------------------------------------------------------------
// 2. Post-connection background forward to Google Apps Script
// -------------------------------------------------------------
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

curl_exec($ch);
curl_close($ch);
