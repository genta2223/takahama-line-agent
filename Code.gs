/**
 * =========================================================================
 * 高浜町 LINE公式アカウント × AI阪口源太 統合バックエンド (GAS)
 * =========================================================================
 * 機能：
 * 1. 現場困りごと通報 (type: "issue") -> スプレッドシート追記 & Googleドライブ画像保存 & メール通知
 * 2. サポーター登録 (type: "supporter") -> スプレッドシート追記 & メール通知
 * 3. LINE Webhook (events) -> Gemini API で「AI阪口源太」として24時間自動応答 (Reply API)
 */

// スクリプトプロパティから認証情報を取得
function getProps() {
  const p = PropertiesService.getScriptProperties();
  return {
    lineAccessToken: p.getProperty('LINE_CHANNEL_ACCESS_TOKEN'),
    geminiApiKey: p.getProperty('GEMINI_API_KEY'),
    adminEmail: p.getProperty('ADMIN_EMAIL') || 'genta2223@gmail.com',
    targetFolderId: p.getProperty('TARGET_FOLDER_ID') || '1sJDx5lyH8n8tdYeDO7BmKzQlCBGDoCKp'
  };
}

/**
 * 初回権限承認用のダミー関数
 * ※GASエディタで「実行」を押して一度承認を完了させてください。
 */
function testAuth() {
  console.log("外部通信(UrlFetchApp)とドライブ(DriveApp)の権限承認テストを実行します");
  try {
    const res = UrlFetchApp.fetch("https://httpbin.org/get", { muteHttpExceptions: true });
    console.log("UrlFetchApp 疎通成功: " + res.getResponseCode());
  } catch (e) {
    console.error("UrlFetchApp エラー: " + e.toString());
  }
}

/**
 * Webhook受信 (POSTリクエスト)
 */
function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      console.warn("doPost: No postData received");
      return ContentService.createTextOutput(JSON.stringify({ status: "error", message: "No post data" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    const rawContents = e.postData.contents;
    console.log("doPost raw content length: " + rawContents.length);
    const json = JSON.parse(rawContents);
    const props = getProps();

    // -------------------------------------------------------------
    // 分岐 1: LINE Messaging API Webhook (AI源太 チャット自動応答)
    // -------------------------------------------------------------
    if (json.events && Array.isArray(json.events)) {
      console.log("doPost: Matched LINE Webhook (events count: " + json.events.length + ")");
      handleLineEvents(json.events, props);
      return ContentService.createTextOutput(JSON.stringify({ status: "success", type: "line_events" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // -------------------------------------------------------------
    // 分岐 2: 現場困りごと通報フォーム (type: "issue")
    // -------------------------------------------------------------
    if (json.type === "issue") {
      console.log("doPost: Matched Civic Issue Submission");
      handleIssueSubmission(json, props);
      return ContentService.createTextOutput(JSON.stringify({ status: "success", type: "issue" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    // -------------------------------------------------------------
    // 分岐 3: 後援会サポーター登録フォーム (type: "supporter")
    // -------------------------------------------------------------
    if (json.type === "supporter") {
      console.log("doPost: Matched Supporter Registration");
      handleSupporterRegistration(json, props);
      return ContentService.createTextOutput(JSON.stringify({ status: "success", type: "supporter" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    console.warn("doPost: Ignored unknown payload type: " + JSON.stringify(json).slice(0, 150));
    return ContentService.createTextOutput(JSON.stringify({ status: "ignored", message: "Unknown payload type" }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    console.error("doPost Exception: " + err.toString());
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// -----------------------------------------------------------------
// LINE Webhook & Gemini API 応答処理
// -----------------------------------------------------------------
function handleLineEvents(events, props) {
  for (let i = 0; i < events.length; i++) {
    const event = events[i];
    // メッセージイベントかつテキストメッセージのみ対応
    if (event.type === 'message' && event.message && event.message.type === 'text') {
      const userMessage = event.message.text.trim();
      const replyToken = event.replyToken;

      console.log(`LINE Event [${i}]: text="${userMessage}", replyToken="${replyToken}"`);
      
      // Gemini APIでAI応答を生成
      const aiReply = askGeminiSakaguchi(userMessage, props.geminiApiKey);
      console.log("AI Reply generated (length: " + aiReply.length + "): " + aiReply.slice(0, 80) + "...");
      
      // LINE Reply APIで返信
      replyToLine(replyToken, aiReply, props.lineAccessToken);
    } else {
      console.log(`LINE Event [${i}]: Skipped (type=${event.type})`);
    }
  }
}

/**
 * Gemini API (gemini-flash-latest) を呼び出し、阪口源太ペルソナで回答生成
 */
function askGeminiSakaguchi(userQuery, apiKey) {
  if (!apiKey) {
    console.warn("GEMINI_API_KEY is not set in Script Properties.");
    return "温かいメッセージをありがとうございます！青郷出身の阪口源太です。\n\n高浜町の未来や地域の困りごとについて、町民の皆様の声を大切にしながら進めてまいります。\n\n現場の道路・水路・安全対策のご要望は、リッチメニューの「まちの困りごと」フォームからも承っております！";
  }

  const systemPrompt = `あなたは福井県高浜町出身の元地方議会議員・IT技術者「阪口源太（さかぐち げんた）」本人として、高浜町の町民の皆様からの相談や質問に対話形式でお答えするAIアシスタントです。

【阪口源太のペルソナ・出自】
- 氏名: 阪口 源太（さかぐち げんた）
- 出身: 福井県高浜町 青郷地区（せいきょうちく）横津海（よこつみ）出身。実家は地域の生活インフラであった「阪口商店」。
- 学歴: 青郷小学校・高浜中学校・若狭高校卒業。
- 経歴: 民間IT企業経営、東大松尾研修了（深層生成モデル・Physical AI等）、Google/IBM認定プロフェッショナル、元沖縄県与那国町議会議員（地方議会実務・一般質問・予算決算審査の即戦力）。50歳で故郷・高浜町へUターン。
- スローガン: 「安心な高浜を、次世代へ。」「青郷から、高浜の安全と未来をまもる。」

【発音・地名の正確な読み】
- 高浜町: たかはまちょう（「まち」は厳禁）
- 青郷: せいきょう（「あおごう」「せいごう」は厳禁）
- 横津海: よこつみ（「よこづみ」は厳禁）
- 日置: ひき（「ひおき」は厳禁）
- 六路谷: ろくろだに

【基本スタンス（ハイブリッド型政治：80%の安心 × 20%の独自性）】
- 80%の安心・継続: 現町政の良質な施策（保育料・給食費の無償化、地域医療支援など）は100%肯定・強力に後押し。全基金残高約100億円（住民1人あたり約102万円）を過大なハコモノ投資から死守し、将来の医療・福祉・インフラ修繕の財源として守る。青郷の国道27号青葉改良、南山手線延伸、六路谷踏切改良などを推進。
- 20%の独自性: 東大松尾研等のAI/IT知見と元地方議員の実務経験を生かした政策。子育て無償化の出口戦略（若者が戻れる空き家改修・家財整理補助やテレワーク拠点）、迷わない窓口設計（LINEや音声入力による行政AX、職員が対話に向き合う時間をつくる）、免許返納後も安心なAIオンデマンド乗合交通（舞鶴市との生活圏連携強化）。

【対話のトーン・口調】
- 丁寧、腰が低く、誠実かつ温かみのある対話調。
- 「こんにちは！青郷出身の阪口源太です。ご質問ありがとうございます」「〜ですね。現場の声を大切にしながら進めてまいります」など、親しみやすく礼儀正しい言葉遣い。
- 感情論や批判ではなく、データと現場感覚に基づき論理的かつ具体的に回答する。

【厳格な安全弁・ガードレール】
1. 公職選挙法上の事前運動の禁止: 「選挙で私に投票してください」「清き一票を」等の直接的な投票依頼は絶対に言わないこと。あくまで「政策広報・後援会活動としての意見交換・地域対話」の枠組みを厳守すること。
2. 個人攻撃・誹謗中傷の排除: 現職町長や他の町議会議員への個人攻撃や批判は絶対に行わない。常に敬意を払い、「良い施策は賛成し、課題があれば専門知見から具体的代替案を提案する」立場を徹底すること。
3. 原発スタンス: 現稼働4基を前提とし、「100億円基金の堅守」「サイバーセキュリティ防衛」「青葉改良や南山手線など避難道路の確保」という実務的・町民の安心安全最優先の観点で答弁し、国政レベルのイデオロギー論争は中立を守ること。
4. 未登録の個別苦情・回答困難な陳情への対応:
   AIで判断できない複雑な個別トラブル、境界問題、プライベートな陳情、または事実確認が必要な事象については、適当な回答を捏造せず、「大変重要かつ切実なご指摘をいただき、ありがとうございます。この件につきましては、私（阪口源太）本人が直接現場を確認し、調査・検討させていただきます。よろしければリッチメニューの『まちの困りごと』フォームから写真や詳細をお寄せいただくか、後援会事務所までご連絡いただければ幸いです」と丁寧に本人フォローへトスアップすること。
5. 文字数: LINEのトーク画面で読みやすいよう、200〜400文字程度を目安に、要点を分かりやすく段落分けして回答すること。`;

  // 確実に稼働する gemini-flash-latest を使用
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${apiKey}`;
  const payload = {
    system_instruction: {
      parts: [{ text: systemPrompt }]
    },
    contents: [
      { role: "user", parts: [{ text: userQuery }] }
    ],
    generationConfig: {
      temperature: 0.4,
      maxOutputTokens: 800
    }
  };

  try {
    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();
    const responseText = response.getContentText();

    if (code !== 200) {
      console.error(`Gemini API HTTP Error: status=${code}, body=${responseText.slice(0, 200)}`);
      return "温かいメッセージをありがとうございます！青郷出身の阪口源太です。\n\n高浜町の未来や地域の困りごとについて、町民の皆様の声を大切にしながら進めてまいります。ご意見・ご要望はお気軽にどうぞ！";
    }

    const data = JSON.parse(responseText);
    if (data.candidates && data.candidates[0] && data.candidates[0].content) {
      return data.candidates[0].content.parts[0].text.trim();
    }
    console.warn("Gemini unexpected JSON response: " + responseText.slice(0, 150));
    return "温かいメッセージをありがとうございます！青郷出身の阪口源太です。\n\n高浜町の未来や地域の困りごとについて、町民の皆様の声を大切にしながら政策に反映させてまいります。ご意見・ご要望はお気軽にどうぞ！";
  } catch (err) {
    console.error("Gemini API Exception: " + err.toString());
    return "メッセージをいただきありがとうございます。阪口源太です。\n\nただいま通信環境によりAI応答が一時的に繋がりにくくなっております。いただいた内容は記録しておりますので、私自身が確認し、活動の参考にさせていただきます！";
  }
}

/**
 * LINE Messaging API (Reply) 送信
 */
function replyToLine(replyToken, messageText, channelAccessToken) {
  if (!channelAccessToken || !replyToken) {
    console.warn("replyToLine: Missing channelAccessToken or replyToken");
    return;
  }

  const url = "https://api.line.me/v2/bot/message/reply";
  const payload = {
    replyToken: replyToken,
    messages: [
      {
        type: "text",
        text: messageText,
        quickReply: {
          items: [
            {
              type: "action",
              action: {
                type: "message",
                label: "🛡️ 100億円基金",
                text: "100億円の基金をどう守る？"
              }
            },
            {
              type: "action",
              action: {
                type: "message",
                label: "🛣️ 青郷の道路",
                text: "青郷の国道27号青葉改良について教えて"
              }
            },
            {
              type: "action",
              action: {
                type: "message",
                label: "👶 子育て支援",
                text: "子育て無償化と若者Uターン策は？"
              }
            },
            {
              type: "action",
              action: {
                type: "message",
                label: "🤖 行政AX",
                text: "AIを使った迷わない役場窓口とは？"
              }
            }
          ]
        }
      }
    ]
  };

  const options = {
    method: "post",
    headers: {
      "Authorization": "Bearer " + channelAccessToken
    },
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const res = UrlFetchApp.fetch(url, options);
    const code = res.getResponseCode();
    const body = res.getContentText();
    if (code !== 200) {
      console.error(`LINE Reply API Error: status=${code}, body=${body}`);
    } else {
      console.log(`LINE Reply API Success: status=${code}`);
    }
  } catch (e) {
    console.error("LINE Reply API Exception: " + e.toString());
  }
}

// -----------------------------------------------------------------
// 現場困りごと通報 処理
// -----------------------------------------------------------------
function handleIssueSubmission(data, props) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName("困りごと通報");
  if (!sheet) {
    sheet = ss.insertSheet("困りごと通報");
    sheet.appendRow(["受付日時", "地区", "カテゴリ", "詳細", "写真URL", "連絡先・名前"]);
    sheet.setFrozenRows(1);
  }

  let imageUrl = data.image_url || "";

  // Base64画像が送られてきた場合、Googleドライブの「現場写真」フォルダに保存
  if (data.image_base64 && data.image_base64.length > 50) {
    try {
      const parentFolder = DriveApp.getFolderById(props.targetFolderId);
      let photoFolder;
      const folders = parentFolder.getFoldersByName("現場写真");
      if (folders.hasNext()) {
        photoFolder = folders.next();
      } else {
        photoFolder = parentFolder.createFolder("現場写真");
      }

      const decodedBytes = Utilities.base64Decode(data.image_base64);
      const mime = data.image_mime || "image/jpeg";
      const fileName = data.image_name || `issue_${Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyyMMdd_HHmmss")}.jpg`;
      const blob = Utilities.newBlob(decodedBytes, mime, fileName);
      const file = photoFolder.createFile(blob);
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
      imageUrl = file.getUrl();
    } catch (driveErr) {
      console.error("Drive save error: " + driveErr.toString());
      imageUrl = "Drive保存エラー: " + driveErr.toString();
    }
  }

  const timestamp = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy/MM/dd HH:mm:ss");
  sheet.appendRow([
    timestamp,
    data.district || "",
    data.category || "",
    data.details || "",
    imageUrl,
    data.contact || ""
  ]);

  // 管理者へメール通知
  if (props.adminEmail) {
    const subject = `【高浜町LINE現場通報】[${data.district || "未選択"}] ${data.category || ""}`;
    const body = `【高浜町 LINE公式 現場通報を受信しました】\n\n` +
      `■ 受信日時: ${timestamp}\n` +
      `■ 地区: ${data.district || "未選択"}\n` +
      `■ カテゴリ: ${data.category || ""}\n` +
      `■ 報告者・連絡先: ${data.contact || "匿名"}\n` +
      `■ 現場写真URL: ${imageUrl}\n\n` +
      `■ 詳細内容:\n${data.details || ""}\n\n` +
      `--------------------------------------------------\n` +
      `スプレッドシート確認URL:\n${ss.getUrl()}`;
    MailApp.sendEmail(props.adminEmail, subject, body);
  }
}

// -----------------------------------------------------------------
// サポーター登録 処理
// -----------------------------------------------------------------
function handleSupporterRegistration(data, props) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName("サポーター登録");
  if (!sheet) {
    sheet = ss.insertSheet("サポーター登録");
    sheet.appendRow(["受付日時", "お名前", "ご住所", "連絡先", "応援メニュー", "メッセージ"]);
    sheet.setFrozenRows(1);
  }

  const timestamp = Utilities.formatDate(new Date(), "Asia/Tokyo", "yyyy/MM/dd HH:mm:ss");
  const menus = Array.isArray(data.menus) ? data.menus.join(", ") : (data.menus || "");

  sheet.appendRow([
    timestamp,
    data.name || "",
    data.address || "",
    data.contact || "",
    menus,
    data.message || ""
  ]);

  // 管理者へメール通知
  if (props.adminEmail) {
    const subject = `【高浜町後援会】サポーター新規登録: ${data.name || "未設定"} 様`;
    const body = `【阪口源太 後援会サポーターの新規登録を受信しました】\n\n` +
      `■ 受信日時: ${timestamp}\n` +
      `■ お名前: ${data.name || ""} 様\n` +
      `■ ご住所: ${data.address || ""}\n` +
      `■ 連絡先: ${data.contact || ""}\n` +
      `■ 応援メニュー: ${menus}\n\n` +
      `■ 応援メッセージ:\n${data.message || ""}\n\n` +
      `--------------------------------------------------\n` +
      `スプレッドシート確認URL:\n${ss.getUrl()}`;
    MailApp.sendEmail(props.adminEmail, subject, body);
  }
}
