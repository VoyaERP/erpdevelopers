"""Bilingual editorial content, not a list of advertised services or credentials.

Content translations live alongside their English source; native UI chrome still
uses Frappe translations. One renderer and one template serve both topic guides.
"""
from copy import deepcopy
from json import dumps

from erpdevelopers.branding import APP_NAME, EXPECTED_SITE, versioned_public_asset
from erpdevelopers.public_pages import set_public_context

INTRO = {
    "en": "Explore practical ERP development, ERPNext and Frappe guidance from ERP Developers. Start with business requirements, secure integrations and a clear delivery plan, rather than a commitment to one ERP platform.",
    "ar": "استكشف أدلة عملية من ERP Developers حول تطوير أنظمة ERP وERPNext وإطار Frappe. ابدأ بمتطلبات الأعمال والتكاملات الآمنة وخطة تنفيذ واضحة، بدلاً من الالتزام بمنصة واحدة قبل فهم الاحتياج.",
}
LABELS = {
    "en": dict(home="Home", eyebrow="PRACTICAL DEVELOPMENT GUIDES", related="Continue exploring", references="Official documentation", language="Read this guide in", note="An editorial starting point, not a platform certification or a substitute for validating requirements against your installed version."),
    "ar": dict(home="الرئيسية", eyebrow="أدلة عملية للتطوير", related="تابع الاستكشاف", references="الوثائق الرسمية", language="اقرأ هذا الدليل باللغة", note="دليل تمهيدي، وليس اعتماداً من أي منصة أو بديلاً عن التحقق من المتطلبات على الإصدار المثبت لديك."),
}
GUIDES = {
    "erp-development": {
        "en": {
            "title": "ERP Development Guide", "heading": "ERP development that starts with the business process",
            "description": "Plan ERP development across business platforms: requirements, standard versus custom features, integrations, permissions, testing and deployment.",
            "lead": "A useful ERP change solves a defined operational problem without making the next upgrade harder. This guide gives business owners, solution architects and developers a shared starting point for reviewing a change before writing code.",
            "sections": [
                ("Map the process and its exceptions", "Describe who starts the transaction, which master data it uses, who approves it and what the final output must be. Walk through a normal case and an exception, such as a rejected delivery, a cancelled invoice or a partial receipt. Record acceptance criteria in business terms: the action, the permitted user, the expected state and the evidence retained. This becomes the basis for both the design and the test plan."),
                ("Separate configuration from custom development", "Build a gap register before choosing a solution. For each requirement, distinguish a standard feature, configuration, an extension and a separate integration. Compare the recurring maintenance cost, not just the initial build effort. ERPNext, Microsoft Dynamics 365 Business Central, SAP and Odoo are examples of platforms to evaluate; do not assume they share the same extension model, API coverage or licensing. Validate the proposed approach on the actual product version."),
                ("Define data ownership and integration behavior", "Assign an authoritative system to each important entity: customer, supplier, item, price or payment. Specify identifiers, field mappings, validation rules and the point at which an update is accepted. Design retries so a repeated message does not create a second financial or operational transaction. Make reconciliation visible through a status, error reason and source reference. Keep credentials server-side and avoid sending entire records where a limited set of fields is sufficient."),
                ("Make permissions part of the workflow", "Document which roles can create, review, approve, cancel and read each record. A hidden button is not a security boundary: the server must enforce the same rules. Include company restrictions and private attachments in the design. Where maker-checker separation is required, test that the creator cannot approve their own entry, including when an API is used. Choose defaults that do not expose draft records to public pages."),
                ("Test the release, not only the happy path", "Use a representative test site to verify positive and negative scenarios, translations, reporting and performance. Check the consequences of editing, cancellation and repeated integration requests. Before deployment, record the exact application revision, back up the affected site and define recovery steps. Afterward, verify the rendered pages and application responses; a successful build or a running process alone is not proof that the feature works."),
            ],
        },
        "ar": {
            "title": "دليل تطوير أنظمة ERP", "heading": "تطوير أنظمة ERP يبدأ من إجراءات العمل",
            "description": "خطط لتطوير أنظمة ERP: المتطلبات والوظائف القياسية والتخصيص والتكاملات والصلاحيات والاختبارات والنشر عبر منصات الأعمال المختلفة.",
            "lead": "التعديل الناجح يعالج مشكلة تشغيلية محددة دون تعقيد التحديث التالي. يقدم هذا الدليل نقطة انطلاق مشتركة لأصحاب الأعمال ومهندسي الحلول والمطورين لمراجعة التغيير قبل كتابة الكود.",
            "sections": [
                ("حدد الإجراء وحالاته الاستثنائية", "وضح من يبدأ المعاملة، وما البيانات الأساسية المستخدمة، ومن يعتمدها، وما المخرجات المطلوبة. راجع حالة طبيعية وأخرى استثنائية، مثل رفض تسليم أو إلغاء فاتورة أو استلام جزئي. اكتب معايير القبول بلغة الأعمال: الإجراء والمستخدم المسموح له والحالة المتوقعة والمستندات المحتفظ بها. تصبح هذه المعايير أساساً للتصميم وخطة الاختبار."),
                ("افصل الإعداد عن التطوير المخصص", "أنشئ سجل فجوات قبل اختيار الحل. صنف كل متطلب إلى وظيفة قياسية أو إعداد أو إضافة برمجية أو تكامل مستقل. قارن تكلفة الصيانة المتكررة، لا تكلفة التطوير الأولى فقط. من المنصات التي يمكن تقييمها ERPNext وMicrosoft Dynamics 365 Business Central وSAP وOdoo، لكن لا تفترض تشابه نماذج التوسعة أو واجهات API أو التراخيص بينها. تحقق من النهج المقترح على إصدار المنتج الفعلي."),
                ("حدد مسؤولية البيانات وسلوك التكامل", "عين النظام المرجعي لكل كيان مهم، مثل العميل والمورد والصنف والسعر والدفع. حدد المعرفات وربط الحقول وقواعد التحقق ووقت قبول التحديث. صمم إعادة المحاولة بحيث لا تنشئ الرسالة المكررة معاملة مالية أو تشغيلية ثانية. أظهر حالة المطابقة وسبب الخطأ ومرجع المصدر. احتفظ ببيانات الاتصال السرية على الخادم، ولا ترسل سجلاً كاملاً عندما تكفي حقول محددة."),
                ("اجعل الصلاحيات جزءاً من دورة العمل", "وثق الأدوار المسموح لها بالإنشاء والمراجعة والاعتماد والإلغاء والقراءة. إخفاء الزر ليس حاجزاً أمنياً؛ يجب تطبيق القواعد نفسها على الخادم. ضمّن قيود الشركات والمرفقات الخاصة في التصميم. وعند اشتراط الفصل بين المنشئ والمعتمد، اختبر عدم قدرة المنشئ على اعتماد سجله، حتى عبر API. اختر إعدادات افتراضية لا تكشف المسودات في الصفحات العامة."),
                ("اختبر الإصدار وحالات الفشل", "استخدم موقع اختبار ممثلاً للعمل الفعلي للتحقق من السيناريوهات الإيجابية والسلبية والترجمة والتقارير والأداء. راجع أثر التعديل والإلغاء وتكرار طلبات التكامل. قبل النشر، سجل المراجعة البرمجية الدقيقة وخذ نسخة احتياطية من الموقع وحدد خطوات الاستعادة. وبعد النشر، تحقق من الصفحات واستجابات التطبيق؛ نجاح البناء أو تشغيل العملية وحده لا يثبت أن الوظيفة تعمل."),
            ],
        },
        "references": [],
    },
    "erpnext-development": {
        "en": {
            "title": "ERPNext Development & Frappe Guide", "heading": "ERPNext development with a clear Frappe foundation",
            "description": "Understand ERPNext development with Frappe: DocTypes, custom apps, permissions, REST integrations and a practical release checklist.",
            "lead": "ERPNext development combines business-process understanding with Frappe's application model. The aim is not to recreate standard ERP behavior, but to identify a genuine gap and implement the smallest maintainable extension. Use the official references below alongside the documentation for your installed release.",
            "sections": [
                ("Start with the DocType and record lifecycle", "Frappe uses DocTypes to describe an application's data model, fields and associated behavior. Before adding a new one, check whether an existing ERPNext record already represents the business concept. Define the links to master data and the permitted transitions between states. For an extension, decide which values are entered by the user and which should be derived. Avoid storing the same business fact in several places without an explicit ownership rule."),
                ("Choose configuration or a separate app deliberately", "Write down the requirement and reproduce it on a test site before deciding how to implement it. Our recommended approach is to keep reusable custom business logic in a version-controlled app and use documented extension points, rather than silently editing framework files. Document the Frappe and ERPNext versions tested. A feature validated on one major version should not be advertised as compatible with another without separate checks."),
                ("Enforce access on the server", "Frappe's permissions model supports role-based access and additional user restrictions. Test the permissions required for the actual operation, not just whether a menu or button appears. For a public website, expose only an explicit set of published fields; do not make a business DocType guest-readable simply to display a card. Treat private attachments, company access and draft records as separate test cases."),
                ("Build integrations around documented APIs", "Frappe provides REST access to documents and methods, with authentication options described in its official API documentation. Use a dedicated integration identity with the minimum required permissions. Define external identifiers, bounded requests, timeout behavior and reconciliation. Keep tokens out of browser code and logs. Test repeated and out-of-order requests before accepting an integration that can create invoices, payments or stock movements."),
                ("Include migration and browser checks in acceptance", "Our recommended release checklist includes code validation, permissions tests, representative workflow tests, a site backup and a reviewed application revision. Run migrations and build the assets required by the release. Then verify actual HTTP responses and the frontend in Arabic and English. Check that translations, links and scripts are delivered from the intended version, and confirm that a restart has reached application readiness before calling the release complete."),
            ],
        },
        "ar": {
            "title": "دليل تطوير ERPNext وFrappe", "heading": "تطوير ERPNext على أساس واضح من Frappe",
            "description": "تعرف على تطوير ERPNext باستخدام Frappe: أنواع المستندات والتطبيقات المخصصة والصلاحيات وتكاملات REST وخطوات التحقق من الإصدار.",
            "lead": "يجمع تطوير ERPNext بين فهم إجراءات الأعمال ونموذج التطبيقات في Frappe. الهدف ليس إعادة بناء وظائف ERP القياسية، بل تحديد فجوة حقيقية وتنفيذ أصغر إضافة قابلة للصيانة. استخدم المراجع الرسمية أدناه مع وثائق إصدارك المثبت.",
            "sections": [
                ("ابدأ بنوع المستند ودورة حياة السجل", "يستخدم Frappe أنواع المستندات DocTypes لوصف نموذج بيانات التطبيق وحقوله وسلوكه. قبل إضافة نوع جديد، تحقق مما إذا كان سجل موجود في ERPNext يمثل المفهوم المطلوب. حدد روابط البيانات الأساسية والانتقالات المسموح بها بين الحالات. ميز بين القيم التي يدخلها المستخدم والقيم المحسوبة. تجنب تخزين حقيقة الأعمال نفسها في أماكن متعددة دون قاعدة واضحة تحدد مصدرها المرجعي."),
                ("اختر الإعداد أو التطبيق المستقل بوضوح", "وثق المتطلب وأعد تنفيذه على موقع اختبار قبل اختيار أسلوب التطوير. نوصي بحفظ منطق الأعمال المخصص القابل لإعادة الاستخدام في تطبيق خاضع لإدارة الإصدارات، واستخدام نقاط التوسعة الموثقة بدلاً من تعديل ملفات الإطار مباشرة. سجل إصداري Frappe وERPNext اللذين أجريت عليهما الاختبار. لا تعلن توافق وظيفة مع إصدار رئيسي آخر دون تحقق مستقل."),
                ("طبق ضوابط الوصول على الخادم", "يدعم نموذج صلاحيات Frappe الوصول حسب الأدوار وقيود المستخدم الإضافية. اختبر صلاحيات العملية نفسها، لا مجرد ظهور القائمة أو الزر. في الموقع العام، اعرض حقولاً منشورة ومحددة صراحة؛ ولا تمنح الزائر قراءة نوع مستند أعمال كاملاً لمجرد عرض بطاقة. اختبر المرفقات الخاصة وقيود الشركة والمسودات كلّاً على حدة."),
                ("ابنِ التكامل على واجهات موثقة", "يوفر Frappe الوصول إلى المستندات والوظائف عبر REST، وتوضح وثائقه الرسمية خيارات المصادقة. استخدم هوية تكامل مستقلة بأقل الصلاحيات المطلوبة. حدد المعرفات الخارجية وحدود الطلبات ومهلة الاتصال وآلية المطابقة. أبقِ الرموز السرية خارج كود المتصفح والسجلات. اختبر الطلبات المتكررة وغير المرتبة قبل قبول تكامل ينشئ فواتير أو دفعات أو حركات مخزون."),
                ("ضمّن الترحيل واختبار المتصفح في القبول", "تشمل قائمة الإصدار التي نوصي بها فحص الكود واختبارات الصلاحيات ودورات العمل ونسخة احتياطية ومراجعة برمجية معتمدة. نفذ الترحيل وابنِ الملفات اللازمة للإصدار، ثم تحقق من استجابات HTTP الفعلية والواجهة بالعربية والإنجليزية. تأكد من تحميل الترجمة والروابط والبرامج النصية من الإصدار المقصود، وأن التطبيق أصبح جاهزاً بعد إعادة التشغيل قبل إعلان اكتمال النشر."),
            ],
        },
        "references": [
            ("Frappe: Understanding DocTypes", "https://docs.frappe.io/framework/user/en/basics/doctypes"),
            ("Frappe: Users and Permissions", "https://docs.frappe.io/framework/user/en/basics/users-and-permissions"),
            ("Frappe: REST API", "https://docs.frappe.io/framework/user/en/api/rest"),
        ],
    },
}


def guide_links():
    return [dict(slug=slug, title=page["en"]["title"], title_ar=page["ar"]["title"],
                 summary=page["en"]["description"], summary_ar=page["ar"]["description"])
            for slug, page in GUIDES.items()]


def set_guide_context(context, slug, lang="en"):
    if slug not in GUIDES:
        raise ValueError("Unknown editorial guide")
    lang = "ar" if str(lang).lower().startswith("ar") else "en"
    page = deepcopy(GUIDES[slug][lang])
    set_public_context(context, slug=slug, title=page["title"], description=page["description"])
    base = f"https://{EXPECTED_SITE}/{slug}"
    canonical = f"{base}?_lang={lang}"
    context.title = f'{page["title"]} | {APP_NAME}'
    context.canonical_url = canonical
    context.metatags.update({"og:url": canonical, "robots": "index, follow, max-image-preview:large"})
    context.guide = page
    context.guide_labels = dict(LABELS[lang])
    context.guide_references = GUIDES[slug]["references"]
    context.guide_language = lang
    context.guide_links = [dict(href=f'/{key}?_lang={lang}', title=value[lang]["title"])
                           for key, value in GUIDES.items() if key != slug]
    context.discovery_css_url = versioned_public_asset("css/discovery.css")
    context.language_alternates = [dict(lang=code, href=f"{base}?_lang={code}") for code in ("en", "ar")]
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": canonical + "#page", "url": canonical,
         "name": page["heading"], "description": page["description"], "inLanguage": lang,
         "isPartOf": {"@id": f"https://{EXPECTED_SITE}/#website"},
         "publisher": {"@id": f"https://{EXPECTED_SITE}/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": LABELS[lang]["home"], "item": f"https://{EXPECTED_SITE}/"},
            {"@type": "ListItem", "position": 2, "name": page["title"], "item": canonical},
        ]},
    ]}
    context.guide_schema_json = dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
