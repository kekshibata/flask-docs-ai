<template>
  <el-container>
    <el-header>
      <h2>PDF要約</h2>
    </el-header>
    <el-main>
      <el-upload
        ref="upload"
        action="#"
        drag
        :auto-upload="false"
        :file-list="files"
        :on-change="uploadFiles"
        :show-file-list="false"
        :http-request="() => {}"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">
          ドラッグ&ドロップ または <em>クリックしてアップロード</em>する
        </div>
        <div slot="tip" class="el-upload__tip">
          PDFファイルのみアップロード可能です
        </div>
      </el-upload>
      <div class="input-group">
        <label for="word-count">文字数： </label>
        <input id="char-count" type="number" v-model="charCount" min="1" />
      </div>
      <el-progress
        v-if="uploading"
        :percentage="uploadProgress"
        status="success"
      ></el-progress>
      <el-alert
        v-if="uploadSuccess"
        title="ファイルのアップロードに成功しました"
        type="success"
        :closable="false"
      ></el-alert>
      <div v-if="processing" class="processing-text">
        処理中<span class="dots">{{ processingDots }}</span>
      </div>
      <el-typography v-if="summary" style="margin-top: 20px">
        <el-typography-item :level="4">要約</el-typography-item>
      </el-typography>
      <el-input
        v-if="summary"
        type="textarea"
        :rows="5"
        :readonly="true"
        :value="summary"
        placeholder="Summary"
      ></el-input>
      <el-typography v-if="extractedText" style="margin-top: 20px">
        <el-typography-item :level="4">テキスト</el-typography-item>
      </el-typography>
      <el-input
        v-if="extractedText"
        type="textarea"
        :rows="5"
        :readonly="true"
        :value="extractedText"
      ></el-input>
    </el-main>
  </el-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      uploading: false,
      uploadProgress: 0,
      uploadSuccess: false,
      processing: false,
      processingDots: "",
      extractedText: "",
      summary: "",
      charCount: 300,
    };
  },
  methods: {
    updateProcessingDots() {
      this.processingDots = ".".repeat((this.processingDots.length % 3) + 1);
    },
    async uploadFiles(file) {
      this.uploading = true;
      this.uploadProgress = 0;
      this.uploadSuccess = false;

      const formData = new FormData();
      formData.append("file", file.raw);
      formData.append("charCount", this.charCount);

      try {
        const { data } = await axios.post(
          "http://localhost:5000/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
            onUploadProgress: (progressEvent) => {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
            },
          }
        );

        this.uploading = false;
        this.uploadSuccess = true;
        this.processing = true;

        const filename = data.filename;
        const file_id = data.file_id;

        let processingTimer = setInterval(this.updateProcessingDots, 500);

        const response = await axios.get("http://localhost:5000/process", {
          params: {
            filename,
            file_id,
          },
        });

        clearInterval(processingTimer);
        this.processing = false;

        if (response.status === 200) {
          console.log(response.data);
          if (response.data.text && response.data.summary) {
            this.extractedText = response.data.text;
            this.summary = response.data.summary;
          }
        }
      } catch (error) {
        console.error("Upload failed:", error);
      } finally {
        this.uploading = false;
        this.processing = false;
      }
    },
  },
};
</script>

<style scoped>
.processing-text {
  font-size: 0.8em;
  margin-top: 1em;
}
</style>
