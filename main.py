<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>數據管理系統</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <script>
        // 上傳檔案
        async function uploadFile(event) {
            event.preventDefault();
            const form = document.getElementById('uploadForm');
            const resultDiv = document.getElementById('result');
            const formData = new FormData(form);

            try {
                const response = await fetch('http://127.0.0.1:5001/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                resultDiv.innerHTML = response.ok
                    ? `<div class="alert alert-success">${data.success}</div>`
                    : `<div class="alert alert-danger">${data.error}</div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="alert alert-danger">連線失敗: ${error.message}</div>`;
            }
        }

        // 手動輸入
        async function submitInput(event) {
            event.preventDefault();
            const resultDiv = document.getElementById('result');
            const data = {
                id: document.getElementById('inputId').value,
                amount: parseFloat(document.getElementById('amount').value),
                year: parseInt(document.getElementById('inputYear').value),
                month: parseInt(document.getElementById('inputMonth').value),
                store: document.getElementById('inputStore').value
            };

            try {
                const response = await fetch('http://127.0.0.1:5001/input', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                resultDiv.innerHTML = response.ok
                    ? `<div class="alert alert-success">${result.success}</div>`
                    : `<div class="alert alert-danger">${result.error}</div>`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="alert alert-danger">連線失敗: ${error.message}</div>`;
            }
        }

        // 篩選資料
        async function filterData(event) {
            event.preventDefault();
            const year = document.getElementById('year').value;
            const month = document.getElementById('month').value;
            const store = document.getElementById('store').value;
            const resultDiv = document.getElementById('filterResult');

            try {
                const response = await fetch(`http://127.0.0.1:5001/filter_temp?year=${year}&month=${month}&store=${store}`);
                const data = await response.json();
                if (response.ok) {
                    let html = '<table class="table table-striped"><thead><tr><th>ID</th><th>金額</th><th>年份</th><th>月份</th><th>門市</th></tr></thead><tbody>';
                    data.forEach(row => {
                        html += `<tr><td>${row.id}</td><td>${row.amount}</td><td>${row.year}</td><td>${row.month}</td><td>${row.store}</td></tr>`;
                    });
                    html += '</tbody></table>';
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="alert alert-danger">篩選失敗: ${error.message}</div>`;
            }
        }
    </script>
</head>
<body>
    <div class="container mt-4">
        <h1>數據管理系統</h1>

        <!-- 上傳表單 -->
        <h3>上傳檔案</h3>
        <form id="uploadForm" onsubmit="uploadFile(event)">
            <div class="mb-3">
                <label for="fileInput" class="form-label">選擇 CSV 或 Excel 檔案</label>
                <input type="file" class="form-control" id="fileInput" name="file" accept=".csv, .xlsx" required>
            </div>
            <button type="submit" class="btn btn-primary">上傳並暫存</button>
        </form>

        <!-- 手動輸入表單 -->
        <h3 class="mt-5">手動輸入</h3>
        <form id="inputForm" onsubmit="submitInput(event)">
            <div class="row mb-3">
                <div class="col">
                    <input type="text" class="form-control" id="inputId" placeholder="ID" required>
                </div>
                <div class="col">
                    <input type="number" step="0.01" class="form-control" id="amount" placeholder="金額" required>
                </div>
                <div class="col">
                    <input type="number" class="form-control" id="inputYear" placeholder="年份 (如 2023)" required>
                </div>
                <div class="col">
                    <input type="number" class="form-control" id="inputMonth" placeholder="月份 (1-12)" required>
                </div>
                <div class="col">
                    <input type="text" class="form-control" id="inputStore" placeholder="門市 (如 StoreA)" required>
                </div>
            </div>
            <button type="submit" class="btn btn-primary">儲存到暫存</button>
        </form>
        <div id="result" class="mt-3"></div>

        <!-- 篩選表單 -->
        <h3 class="mt-5">篩選暫存資料</h3>
        <form onsubmit="filterData(event)">
            <div class="row mb-3">
                <div class="col">
                    <input type="number" class="form-control" id="year" placeholder="年份 (如 2023)">
                </div>
                <div class="col">
                    <input type="number" class="form-control" id="month" placeholder="月份 (1-12)">
                </div>
                <div class="col">
                    <input type="text" class="form-control" id="store" placeholder="門市 (如 StoreA)">
                </div>
            </div>
            <button type="submit" class="btn btn-primary">篩選</button>
        </form>
        <div id="filterResult" class="mt-3"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>