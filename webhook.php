<?php
require 'config.php';
require 'functions.php';

$content = file_get_contents("php://input");
$update = json_decode($content, true);

if (!$update) exit;

$message = $update['message'] ?? null;
if (!$message) exit;

$text = $message['text'] ?? '';
$chat_id = $message['chat']['id'];
$user_id = $message['from']['id'];
$first_name = $message['from']['first_name'];

$data = loadData();

if ($text === '/start') {
    $menu = in_array($user_id, ADMINS)
        ? [['➕ ثبت چالش'], ['💸 ثبت شاباش'], ['📋 نتایج']]
        : [['📋 نتایج']];
    sendMessage($chat_id, "سلام $first_name 👋\nاز منو گزینه مورد نظر رو انتخاب کن:", $menu);
}

elseif ($text === '➕ ثبت چالش' && in_array($user_id, ADMINS)) {
    sendMessage($chat_id, "لطفا عنوان چالش را به این صورت ارسال کن:\n\n<code>چالش: اسم_چالش</code>");
}

elseif (strpos($text, "چالش:") === 0 && in_array($user_id, ADMINS)) {
    $name = trim(str_replace("چالش:", "", $text));
    $data['lotteries'][] = [
        'name' => $name,
        'host' => $first_name,
        'date' => date('Y/m/d')
    ];
    saveData($data);
    sendMessage($chat_id, "✅ چالش <b>$name</b> ثبت شد.");
}

elseif ($text === '💸 ثبت شاباش' && in_array($user_id, ADMINS)) {
    sendMessage($chat_id, "لطفا اطلاعات شاباش را به این صورت وارد کن:\n\n<code>شاباش: از طرف_نام, مبلغ_1000, برای_نام</code>");
}

elseif (strpos($text, "شاباش:") === 0 && in_array($user_id, ADMINS)) {
    $parts = explode(',', trim(str_replace("شاباش:", "", $text)));
    if (count($parts) == 3) {
        list($sponsor, $amount, $receiver) = array_map('trim', $parts);
        $lotteries = $data['lotteries'];
        $last_lottery = end($lotteries)['name'] ?? 'نامشخص';
        $data['shabash'][] = [
            'sponsor' => $sponsor,
            'amount' => $amount,
            'receiver' => $receiver,
            'lottery_name' => $last_lottery
        ];
        saveData($data);
        sendMessage($chat_id, "✅ شاباش ثبت شد.");
    } else {
        sendMessage($chat_id, "❌ فرمت اشتباه است. دوباره وارد کن.");
    }
}

elseif ($text === '📋 نتایج') {
    $response = "";

    $lotteries = $data['lotteries'];
    $shabash = $data['shabash'];

    if (!$lotteries) {
        $response .= "❌ هنوز چالشی ثبت نشده.\n";
    } else {
        $last = end($lotteries);
        $response .= "📋 <b>آخرین چالش</b>:\n";
        $response .= "🏷 نام: {$last['name']}\n";
        $response .= "👤 گرداننده: {$last['host']}\n";
        $response .= "📅 تاریخ: {$last['date']}\n";
    }

    if ($shabash) {
        $response .= "\n📣 <b>شاباش‌ها</b>:\n";
        foreach ($shabash as $s) {
            $response .= "از طرف {$s['sponsor']} مبلغ {$s['amount']} تومان برای {$s['receiver']} (چالش: {$s['lottery_name']})\n";
        }
    }

    sendMessage($chat_id, $response ?: "📭 هنوز اطلاعاتی موجود نیست.");
}

else {
    sendMessage($chat_id, "دستور ناشناس بود. لطفاً از منو انتخاب کن.");
}
