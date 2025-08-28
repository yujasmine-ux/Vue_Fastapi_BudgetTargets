<template>
  <div id="app">
    <h1>資料同步中心</h1>

    <section class="card">
      <h2>上傳 CSV/Excel 檔案</h2>
      <input type="file" @change="handleFileChange" accept=".csv, .xls, .xlsx">
      <button @click="uploadFile" :disabled="!file">上傳並同步</button>
      <p v-if="uploadStatus">{{ uploadStatus }}</p>
    </section>

    <section class="card">
      <h2>手動輸入資料</h2>
      <div v-for="(item, index) in manualData" :key="index" class="data-row">
        <input type="text" v-model="item.store_name" placeholder="門市名稱">
        <input type="number" v-model.number="item.year" placeholder="年份">
        <input type="number" v-model.number="item.month" placeholder="月份">
        <input type="number" v-model.number="item.amount" placeholder="金額">
        <button @click="removeItem(index)">移除</button>
      </div>
      <button @click="addItem">新增一筆</button>
      <button @click="submitManualData">提交並同步</button>
      <p v-if="manualStatus">{{ manualStatus }}</p>
    </section>
  </div>
</template>

<script>
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'; // 部署時請在 .env 檔案中設定 VITE_API_URL

export default {
  data() {
    return {
      file: null,
      uploadStatus: '',
      manualData: [{ store_name: '', year: new Date().getFullYear(), month: 1, amount: null }],
      manualStatus: ''
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
      this.uploadStatus = this.file ? `已選取檔案：${this.file.name}` : '';
    },
    async uploadFile() {
      if (!this.file) {
        this.uploadStatus = "請先選擇檔案。";
        return;
      }
      const formData = new FormData();
      formData.append('file', this.file);

      this.uploadStatus = '正在上傳...';
      try {
        const response = await axios.post(`${API_URL}/api/upload-file`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        this.uploadStatus = `同步成功！訊息：${response.data.message}`;
      } catch (error) {
        this.uploadStatus = `同步失敗：${error.response?.data?.detail || error.message}`;
      }
    },
    addItem() {
      this.manualData.push({ store_name: '', year: new Date().getFullYear(), month: new Date().getMonth() + 1, amount: null });
    },
    removeItem(index) {
      this.manualData.splice(index, 1);
    },
    async submitManualData() {
      this.manualStatus = '正在同步...';
      try {
        const response = await axios.post(`${API_URL}/api/manual-sync`, this.manualData);
        this.manualStatus = `同步成功！訊息：${response.data.message}`;
      } catch (error) {
        this.manualStatus = `同步失敗：${error.response?.data?.detail || error.message}`;
      }
    }
  }
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
.card {
  border: 1px solid #ddd;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.data-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
input, button {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}
</style>