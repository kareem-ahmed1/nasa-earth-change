# Earth Trend Explorer — Laravel Architecture Summary (nasa-laravel)

## 1. What the Laravel app is and how it connects to the FastAPI statistics service
- **Role**: `nasa-laravel` serves as the user-facing web interface and authenticated application layer, completely shielding the Python backend from public browser access.
- **Connection**: It connects to the FastAPI statistics microservice (`http://127.0.0.1:8001`) via Laravel's HTTP Client (`Http::timeout()`), configured through the `.env` variable `ANALYSIS_API_URL` within `App\Services\AnalysisService`.

## 2. Main pages and API routes
- **Web Pages**:
  - `/` (`welcome.blade.php`): Scientific landing page detailing the mission, the 4 core questions, data provenance (NASA GISTEMP & MERRA-2), methodology, and limitations.
  - `/dashboard` (`dashboard.blade.php`): Primary interactive workspace with the Leaflet Africa map, controls, Plotly charts, and statistical test outputs.
  - Auth routes: Standard authentication and profile management routes (`/profile`, `/login`, `/register`).
- **Internal API Routes (`routes/api.php`)**:
  - `GET /api/regions`: Returns canonical African macro-regions and coverage years (2004–2024).
  - `GET /api/variables`: Returns variable definitions, scientific units, and data sources.
  - `GET|POST /api/analyze`: Proxies query parameters to FastAPI `/analysis` and `/charts`, returning merged statistical metrics, time series, scatter, and regression series.
  - `GET|POST /api/predict`: Proxies requests to FastAPI `/predict` for Model 1 v6 next-month risk inference.

## 3. Dashboard features
- **Variable Selector**: Toggles between Surface Temperature Anomaly (`°C`, NASA GISTEMP v4) and Precipitation (`mm/day`, NASA POWER/MERRA-2) with live metadata updates.
- **Year Pickers**: Bounded start and end year dropdown selectors constrained to the 2004–2024 satellite observation period with validation (`start_year <= end_year`).
- **Map & Region Selection**: Interactive Leaflet map featuring GeoJSON polygons for the 5 African macro-regions (North, West, Central, East, Southern Africa), complete with geodesic area calculations and boundary previews.
- **Analyze & Predict Action Buttons**: Dedicated execution buttons with loading spinners, state tracking, and error messaging.
- **Chart Selector Dropdown**: Toggles between 5 distinct analytical visualizations: *Trending, Mann-Kendall / Sen's slope, Correlation, Linear Regression,* and *Regression (Residuals)*.
- **Chart Explanation Panel**: Collapsible Alpine.js guide directly below the chart, providing 3–5 sentences of technical interpretation and dynamic 1–2 sentence real-data statistical synthesis for the active selection.

## 4. What appears after clicking Analyze and Predict
- **After Clicking "Analyze"**:
  - Reveals the `#analysis-results` section.
  - Renders the interactive Plotly.js chart for the selected chart type with hover tooltips, zoom/pan, and units.
  - Updates the **Statistical Test Results** card: detected trend direction badge, Sen's slope rate (per decade and per year), significance verdict badge at $\alpha = 0.05$, exact p-value, Kendall's $\tau$, sample size $n$, and plain-language scientific interpretation.
  - Displays data provenance, methodology tags, and analytical caveats.
  - Updates the collapsible "How to read this chart" explanation panel with current values.
- **After Clicking "Predict"**:
  - Reveals the `#prediction-results-card` directly beneath the action buttons.
  - Displays the target forecast period (January 2025), Model version (`Model 1 v6`), risk probability percentage, baseline climatological probability, risk lift multiplier, and a color-coded risk tier badge (Elevated / Moderate / Baseline).
  - Outlines the high-anomaly threshold and transparent validation status (validated walk-forward ROC-AUC 0.753 for Temperature; advisory/unvalidated for Precipitation).

## 5. Data flow: user click → Laravel → FastAPI → chart and results
- **User Action**: The user selects a region, variable, year range, and chart type on the dashboard and clicks **Analyze** (or changes the chart type dropdown).
- **Frontend Request**: `resources/js/map/earth-map.js` dispatches an asynchronous fetch request to the Laravel backend route `/api/analyze`.
- **Laravel Proxy & Enrichment**: `AnalysisController::analyze()` validates inputs and delegates to `AnalysisService::analyze()`, which executes concurrent HTTP requests to FastAPI's `/analysis` and `/charts` endpoints, merges the series, formats numbers, and generates a plain-language verdict.
- **FastAPI Calculation**: FastAPI queries `africa_climate_merged_2004_2024.csv`, executes SciPy/Statsmodels routines, and returns calculated results to Laravel.
- **Display**: Laravel responds with a unified JSON payload to the browser; `earth-map.js` invokes `Plotly.newPlot()` and populates the DOM metric nodes and explanation panel.

## 6. Data integrity check
- **Confirmation**: Confirmed that **zero synthetic or fabricated data remains** in the application.
- All mock generator routines (`runDemoAnalysis()`, `Math.sin()`, hardcoded trend rates, and random noise) have been eradicated from `earth-map.js` and the backend. Every number displayed originates from `africa_climate_merged_2004_2024.csv` through the Python engine.

## 7. Known limitations or unfinished items
- **Macro-Regional Averaging**: Spatial resolution is limited to 5 broad continental macro-regions; country-level or pixel-level drill-down is not yet implemented.
- **Autocorrelation Handling**: Mann-Kendall test p-values reflect standard non-parametric ranking without pre-whitening or serial autocorrelation correction.
- **Precipitation Prediction Validation**: While the Temperature exceedance ML model is validated (walk-forward ROC-AUC 0.753), the Precipitation ML prediction remains experimental and advisory.
- **Offline Dependency for CDNs**: Plotly.js (`cdn.plot.ly/plotly-2.35.2.min.js`) and Bunny Fonts load via external CDN links rather than locally bundled vendor packages.

---

# الملخص بالعربي

## 1. ماهية تطبيق Laravel وكيفية اتصاله بخدمة إحصاءات FastAPI
- **الدور**: يعمل `nasa-laravel` كواجهة ويب للمستخدم وطبقة تطبيق مؤمنة، مما يعزل خلفية Python البرمجية تماماً عن وصول المتصفح المباشر.
- **الاتصال**: يتصل التطبيق بخدمة FastAPI الإحصائية المصغرة (`http://127.0.0.1:8001`) عبر عميل Laravel HTTP (`Http::timeout()`)، والمعتمد على المتغير `ANALYSIS_API_URL` من ملف `.env` داخل `App\Services\AnalysisService`.

## 2. الصفحات الرئيسية ومسارات الـ API
- **صفحات الويب**:
  - `/` (`welcome.blade.php`): صفحة الهبوط العلمية التي تشرح مهمة المشروع، والأسئلة الجوهرية الأربعة، ومصادر بيانات NASA (GISTEMP و MERRA-2)، والمنهجية، والقيود العلمية.
  - `/dashboard` (`dashboard.blade.php`): لوحة التحكم التفاعلية الرئيسية التي تضم خريطة إفريقيا التفاعلية عبر Leaflet، وأدوات التحكم، ورسوم Plotly البيانية، ونتائج الاختبارات الإحصائية.
  - مسارات المصادقة: مسارات تسجيل الدخول وإدارة الملف الشخصي القياسية (`/profile`، `/login`، `/register`).
- **مسارات الـ API الداخلية (`routes/api.php`)**:
  - `GET /api/regions`: إرجاع أسماء الأقاليم الإفريقية الخمسة وسنوات التغطية المتاحة (2004–2024).
  - `GET /api/variables`: إرجاع المتغيرات المناخية، ووحداتها العلمية، ومصادر بياناتها.
  - `GET|POST /api/analyze`: تمرير الاستعلامات إلى FastAPI عبر `/analysis` و `/charts`، وإرجاع المؤشرات الإحصائية المدمجة، والسلاسل الزمنية، ونقاط التشتت، وخطوط الانحدار.
  - `GET|POST /api/predict`: تمرير الطلب إلى نموذج Model 1 v6 عبر FastAPI `/predict` للتنبؤ باحتمالية مخاطر الظواهر المناخية للشهر القادم.

## 3. مميزات لوحة التحكم (Dashboard)
- **محدد المتغيرات (Variable Selector)**: التبديل بين شذوذ درجة حرارة السطح (`°C`، NASA GISTEMP v4) ومعدل هطول الأمطار اليومي (`mm/day`، NASA POWER/MERRA-2) مع تحديث فوري لبيانات المصدر والوحدات.
- **محدد السنوات (Year Pickers)**: قوائم منسدلة لاختيار سنة البداية والنهاية محكومة بفترة الرصد عبر الأقمار الصناعية (2004–2024) مع التحقق من صحة الإدخال (`start_year <= end_year`).
- **الخريطة وتحديد الأقاليم**: خريطة Leaflet تفاعلية تحتوي على مضلعات GeoJSON للمناطق الإفريقية الخمس الكبرى (شمال، غرب، وسط، شرق، وجنوب إفريقيا)، مع حساب تلقائي للمساحات الجيوديسية ومعاينة الإحداثيات.
- **أزرار التحليل والتنبؤ (Analyze & Predict)**: أزرار تنفيذ مخصصة تدعم مؤشرات التحميل الدوارة، وتتبع الحالات، والتنبيه التلقائي بالأخطاء.
- **محدد نوع الرسم البياني (Chart Selector)**: قائمة منسدلة للتبديل بين 5 أشكال تحليلية: *Trending، و Mann-Kendall / Sen's slope، و Correlation، و Linear Regression، و Regression (القيم المتبقية Residuals)*.
- **لوحة شرح الرسم البياني (Chart Explanation Panel)**: لوحة قابلة للطي مدعومة بـ Alpine.js أسفل الرسم، تقدم 3 إلى 5 جمل كدليل تقني للباحثين، وجملة إلى جملتين لتركيب النتائج الإحصائية الفعلية للمنطقة المختارة بصورة ديناميكية.

## 4. ما يظهر بعد النقر على Analyze و Predict
- **بعد النقر على "Analyze"**:
  - ظهور قسم النتائج الإحصائية `#analysis-results`.
  - رسم المخطط البياني التفاعلي عبر Plotly.js وفق النوع المختار، متضمناً قراءات التمرير (tooltips)، وأدوات التكبير والتنقل، والوحدات الدقيقة.
  - تحديث بطاقة **نتائج الاختبار الإحصائي**: شارة اتجاه الاتجاه المناخي، ومعدل انحدار Sen's slope (لكل عقد ولكل سنة)، وشارة الحكم الإحصائي عند مستوى دلالة $\alpha = 0.05$، وقيمة p-value الدقيقة، ومعامل Kendall's $\tau$، وحجم العينة $n$، والتفسير العلمي باللغة المبسطة.
  - عرض مصدر البيانات والملاحظات والتحذيرات المنهجية.
  - تحديث لوحة شرح الرسم البياني "How to read this chart" بالقيم الحالية.
- **بعد النقر على "Predict"**:
  - ظهور بطاقة التنبؤ `#prediction-results-card` أسفل أزرار التحكم مباشرة.
  - عرض الفترة الزمنية المستهدفة (يناير 2025)، وإصدار النموذج (`Model 1 v6`)، والنسبة المئوية لاحتمالية الخطر، ونسبة الخطر المناخية الأساسية، ومعدل الارتفاع عن المعدل الطبيعي (Lift)، وشارة مستوى الخطر (Elevated / Moderate / Baseline).
  - توضيح حد الشذوذ المرتفع (Threshold)، وإبراز حالة التحقق بكل شفافية (نموذج الحرارة مدقق باختبار walk-forward برصيد ROC-AUC 0.753، بينما نموذج الأمطار استرشادي فقط وغير مدقق).

## 5. مسار تدفق البيانات: نقرة المستخدم ← Laravel ← FastAPI ← الرسم والنتائج
- **إجراء المستخدم**: يختار المستخدم الإقليم، والمتغير، والسنوات، ونوع الرسم البياني على لوحة التحكم ثم ينقر على **Analyze** (أو يغير نوع الرسم).
- **طلب الواجهة الأمامية**: يرسل ملف `resources/js/map/earth-map.js` طلباً غير متزامن (Fetch API) إلى مسار Laravel الداخلي `/api/analyze`.
- **وساطة ومعالجة Laravel**: يقوم `AnalysisController::analyze()` بالتحقق من المدخلات ثم تفويضها إلى `AnalysisService::analyze()`، والذي يرسل طلبات HTTP متزامنة إلى مسارات FastAPI (`/analysis` و `/charts`)، ويدمج السلاسل، وينسق الأرقام، ويولد التفسير اللفظي المبسط.
- **الحسابات داخل FastAPI**: يقرأ FastAPI ملف `africa_climate_merged_2004_2024.csv`، ويجري العمليات الحسابية عبر مكتبات SciPy و Statsmodels، ثم يعيد النتائج الصافية إلى Laravel.
- **العرض**: يعيد Laravel استجابة JSON موحدة إلى المتصفح؛ فيتولى `earth-map.js` استدعاء `Plotly.newPlot()` لتحديث الرسم وتغذية عناصر الـ DOM ولوحة الشرح بالأرقام المحسوبة.

## 6. التحقق من سلامة البيانات
- **تأكيد قاطع**: تم التأكد بشكل كامل من **عدم وجود أي بيانات وهمية أو مصطنعة نهائياً** داخل التطبيق.
- تم استئصال جميع دوال التوليد الاصطناعي القديمة (`runDemoAnalysis()`، و `Math.sin()`، ومعدلات الاتجاه الثابتة، والضوضاء العشوائية) من ملف `earth-map.js` ومن الواجهة الخلفية. جميع الأرقام المعروضة مستخرجة ومحسوبة مباشرة من ملف `africa_climate_merged_2004_2024.csv` عبر محرك Python.

## 7. القيود الحالية والأمور غير المكتملة
- **التعميم على مستوى الأقاليم الكبرى (Macro-Regional Averaging)**: يقتصر النطاق الجغرافي على 5 أقاليم قارية كبرى؛ ولا تتوفر حالياً إمكانية استعراض البيانات على مستوى الدول الفردية أو الشبكات النقطية الدقيقة.
- **الارتباط الذاتي الزمني (Autocorrelation)**: تعتمد قيم p-value لاختبار Mann-Kendall على الرتب الإحصائية القياسية دون تطبيق تقنيات المعالجة المسبقة للتخلص من الارتباط الذاتي المتسلسل (Pre-whitening).
- **التحقق من نموذج الأمطار**: في حين أن نموذج التنبؤ بالحرارة مدقق إحصائياً باختبار walk-forward (بمعدل ROC-AUC 0.753)، فإن نموذج التنبؤ بالأمطار ما يزال استرشادياً وتجريبياً ولم يتم تدقيقه بنفس المستوى.
- **الاعتماد على شبكات الربط الخارجية (CDNs)**: يتم تحميل Plotly.js وخطوط Bunny Fonts من خلال روابط CDN خارجية بدلاً من حزم محلية مدمجة ضمن المشروع (Offline Bundling).
