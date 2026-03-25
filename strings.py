# Translation strings for Selling Accounts Bot

STRINGS = {
    'ar': {
        'START_MSG_1': "🎉 مرحباً بك في متجر الحسابات! 🛒\n\nهنا يمكنك شراء حسابات جيميل جاهزة وموثوقة.",
        'START_MSG_2': "🎯 اختر من القائمة أدناه للبدء.",
        'BTN_BUY': "🛒 شراء حساب",
        'BTN_BALANCE': "💰 رصيدي",
        'BTN_DEPOSIT': "💵 شحن الرصيد",
        'BTN_MY_ORDERS': "📂 مشترياتي",
        'BTN_HELP': "💬 Help",
        'BTN_SETTINGS': "⚙️ الإعدادات",
        'BTN_LANG': "🌐 اللغة",
        'BTN_BACK': "🔙 رجوع",
        
        # Balance
        'BALANCE_TITLE': "💰 <b>رصيدك الحالي</b>\n\n",
        'BALANCE_INFO': "الرصيد المتاح: <b>{balance:.2f}$</b>\n",
        
        # Deposit
        'DEPOSIT_TITLE': "💵 <b>شحن الرصيد</b>\n\n",
        'DEPOSIT_METHOD_PROMPT': "اختر طريقة الشحن المناسبة لك:",
        'DEPOSIT_AMOUNT_PROMPT': "✅ الطريقة: <b>{method}</b>\n\nأدخل المبلغ المراد شحنه بالدولار (مثال: 5):",
        'DEPOSIT_SENDER_PHONE_PROMPT': "📱 أدخل رقم الهاتف الذي قمت بالتحويل منه (فودافون كاش):",
        'DEPOSIT_INSTRUCTIONS': "📝 <b>تعليمات الشحن:</b>\n\n{instructions}\n\nبعد التحويل، أرسل إثبات التحويل (رقم المعاملة أو صورة):",
        'DEPOSIT_SUCCESS': "✅ تم إرسال طلب الشحن بنجاح!\n\nسيتم مراجعة الطلب من قبل الإدارة وإضافة الرصيد فور التأكد.",
        
        # Shop
        'SHOP_TITLE': "🛒 <b>متجر الحسابات</b>\n\n",
        'SHOP_INFO': "الحسابات المتوفرة: <b>{count}</b>\nسعر الحساب: <b>{price:.2f}$</b>\n",
        'SHOP_PROMPT_BUY': "هل تريد شراء حساب جيميل الآن؟",
        'BTN_CONFIRM_BUY': "✅ تأكيد الشراء",
        'SHOP_SUCCESS': "🎉 <b>تم الشراء بنجاح!</b>\n\n📧 الإيميل: <code>{email}</code>\n🔑 الباسورد: <code>{password}</code>\n{recovery}\n\nيمكنك دائماً العثور على حساباتك في قسم \"مشترياتي\".",
        'SHOP_NO_ACCOUNTS': "⚠️ عذراً، لا توجد حسابات متوفرة حالياً. يرجى المحاولة لاحقاً.",
        'SHOP_INSUFFICIENT': "❌ رصيدك غير كافٍ لشراء هذا الحساب. يرجى شحن الرصيد أولاً.",
        
        # My Orders
        'ORDERS_TITLE': "📂 <b>قائمة مشترياتك ({count})</b>\n\n",
        'ORDERS_EMPTY': "لم تقم بشراء أي حسابات بعد.",
        'ORDERS_ITEM': "📧 <code>{email}</code>\n🔑 <code>{password}</code>\n📅 {date}\n────────────────\n",
        
        # Language
        'LANG_MSG': "🌐 اختر اللغة / Choose Language:",
        
        # Admin
        'ADMIN_ONLY': "⛔ هذا الأمر للأدمن فقط.",
        'ADMIN_NOTIFY_DEPOSIT': "🔔 <b>طلب إيداع جديد</b>\n\nالمستخدم: {user}\nالمبلغ: {amount}$\nالطريقة: {method}\nالرقم المرسل منه: {sender_phone}\nالإثبات: {proof}\n\nللقبول: /approve_dep {id}\nللرفض: /reject_dep {id} السبب",
        'ADMIN_NOTIFY_BUY': "🛍 <b>عملية شراء جديدة</b>\n\nالمستخدم: {user}\nالحساب: {email}\nالسعر: {price}$",
        'ADMIN_HELP': (
            "🛠 <b>لوحة تحكم الأدمن</b>\n\n"
            "إليك الأوامر المتاحة وكيفية استخدامها:\n\n"
            "1️⃣ <b>إضافة حسابات:</b>\n"
            "<code>/add_accounts email1:pass1 email2:pass2</code>\n"
            "استخدم هذا الأمر لإضافة حسابات جديدة للمتجر.\n\n"
            "2️⃣ <b>قبول إيداع:</b>\n"
            "<code>/approve_dep ID</code>\n"
            "لقبول طلب شحن رصيد وإضافة المبلغ لحساب المستخدم.\n\n"
            "3️⃣ <b>رفض إيداع:</b>\n"
            "<code>/reject_dep ID السبب</code>\n"
            "لرفض الطلب مع إعلام المستخدم بالسبب.\n\n"
            "💡 ستصلك إشعارات تلقائية عند كل عملية إيداع أو شراء جديدة."
        ),
        'ADMIN_DASHBOARD_STATS': (
            "📊 <b>Admin Dashboard</b>\n"
            "──────────────────\n"
            "👥 Total Users: <b>{total_users}</b>\n"
            "💰 Total Balance: <b>{total_balance}$</b>\n"
            "📦 Total Accounts: <b>{total_accounts}</b> (<b>{available_accounts}</b> Avail.)\n"
            "🛒 Total Orders: <b>{total_orders}</b>\n"
            "⏳ Pending Deposits: <b>{pending_deposits}</b>"
        ),
        'BTN_ADMIN_PANEL': "🔗 Open Admin Panel",
        'SHOP_BULK_TITLE': "🛍 <b>شراء حسابات بالجملة</b>\n\nاختر الكمية المطلوبة من القائمة أدناه:",
        'BTN_PAY_TOTAL_1': "📕 ادفع {price}$ لـ {qty} حساب",
        'BTN_PAY_TOTAL_N': "📕 ادفع ({price}$) * {qty} حساب = {total}$",
    },
    'en': {
        'START_MSG_1': "🎉 Welcome to the Accounts Store! 🛒\n\nHere you can buy ready and reliable Gmail accounts.",
        'START_MSG_2': "🎯 Choose from the menu below to start.",
        'BTN_BUY': "🛒 Buy Account",
        'BTN_BALANCE': "💰 My Balance",
        'BTN_DEPOSIT': "💵 Top-up Balance",
        'BTN_MY_ORDERS': "📂 My Purchases",
        'BTN_HELP': "💬 Help",
        'BTN_SETTINGS': "⚙️ Settings",
        'BTN_LANG': "🌐 Language",
        'BTN_BACK': "🔙 Back",
        
        # Balance
        'BALANCE_TITLE': "💰 <b>Current Balance</b>\n\n",
        'BALANCE_INFO': "Available Balance: <b>{balance:.2f}$</b>\n",
        
        # Deposit
        'DEPOSIT_TITLE': "💵 <b>Top-up Balance</b>\n\n",
        'DEPOSIT_METHOD_PROMPT': "Choose your preferred payment method:",
        'DEPOSIT_AMOUNT_PROMPT': "✅ Method: <b>{method}</b>\n\nEnter the amount to top-up in USD (e.g., 5):",
        'DEPOSIT_SENDER_PHONE_PROMPT': "📱 Enter the phone number you sent from (Vodafone Cash):",
        'DEPOSIT_INSTRUCTIONS': "📝 <b>Instructions:</b>\n\n{instructions}\n\nAfter transferring, send proof (Transaction ID or screenshot):",
        'DEPOSIT_SUCCESS': "✅ Top-up request submitted successfully!\n\nThe admin will review it and add the balance once confirmed.",
        
        # Shop
        'SHOP_TITLE': "🛒 <b>Accounts Store</b>\n\n",
        'SHOP_INFO': "Available Accounts: <b>{count}</b>\nAccount Price: <b>{price:.2f}$</b>\n",
        'SHOP_PROMPT_BUY': "Do you want to buy a Gmail account now?",
        'BTN_CONFIRM_BUY': "✅ Confirm Purchase",
        'SHOP_SUCCESS': "🎉 <b>Purchase Successful!</b>\n\n📧 Email: <code>{email}</code>\n🔑 Password: <code>{password}</code>\n{recovery}\n\nYou can always find your accounts in 'My Purchases'.",
        'SHOP_NO_ACCOUNTS': "⚠️ Sorry, no accounts are currently available. Please try again later.",
        'SHOP_INSUFFICIENT': "❌ Insufficient balance. Please top-up your balance first.",
        
        # My Orders
        'ORDERS_TITLE': "📂 <b>Your Purchases ({count})</b>\n\n",
        'ORDERS_EMPTY': "You haven't purchased any accounts yet.",
        'ORDERS_ITEM': "📧 <code>{email}</code>\n🔑 <code>{password}</code>\n📅 {date}\n────────────────\n",
        
        # Language
        'LANG_MSG': "🌐 Choose your preferred language:",
        
        # Admin
        'ADMIN_ONLY': "⛔ This command is for admin only.",
        'ADMIN_HELP': (
            "🛠 <b>Admin Control Panel</b>\n\n"
            "Here are the available commands:\n\n"
            "1️⃣ <b>Add Accounts:</b>\n"
            "<code>/add_accounts email1:pass1 email2:pass2</code>\n"
            "Add new accounts to the store.\n\n"
            "2️⃣ <b>Approve Deposit:</b>\n"
            "<code>/approve_dep ID</code>\n"
            "Approve a top-up request.\n\n"
            "3️⃣ <b>Reject Deposit:</b>\n"
            "<code>/reject_dep ID Reason</code>\n"
            "Reject a request with a reason.\n\n"
            "💡 You will receive automatic notifications for new deposits and purchases."
        ),
        'SHOP_BULK_TITLE': "🛍 <b>Bulk Account Purchase</b>\n\nSelect the desired quantity from the list below:",
        'BTN_PAY_TOTAL_1': "📕 PAY {price}$ for {qty} account",
        'BTN_PAY_TOTAL_N': "📕 PAY ({price}$) * {qty} accounts = {total}$",
        'ADMIN_DASHBOARD_STATS': (
            "📊 <b>Admin Dashboard</b>\n"
            "──────────────────\n"
            "👥 Total Users: <b>{total_users}</b>\n"
            "💰 Total Balance: <b>{total_balance}$</b>\n"
            "📦 Total Accounts: <b>{total_accounts}</b> (<b>{available_accounts}</b> Avail.)\n"
            "🛒 Total Orders: <b>{total_orders}</b>\n"
            "⏳ Pending Deposits: <b>{pending_deposits}</b>"
        ),
        'BTN_ADMIN_PANEL': "🔗 Open Admin Panel",
    }
}
