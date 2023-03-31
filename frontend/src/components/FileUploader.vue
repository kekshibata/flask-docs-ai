<!-- <template> -->
<!--   <div> -->
<!--     <div -->
<!--       @dragover.prevent="handleDragOver" -->
<!--       @drop.prevent="handleDrop" -->
<!--       @click="openFileExplorer" -->
<!--       class="drop-zone" -->
<!--     > -->
<!--       クリックしてファイルを選択するか、ここにファイルをドロップしてください。 -->
<!--     </div> -->
<!--     <input -->
<!--       type="file" -->
<!--       ref="fileInput" -->
<!--       @change="handleFileUpload" -->
<!--       style="display: none" -->
<!--       multiple -->
<!--     /> -->
<!--     <div v-if="uploading"> -->
<!--       <progress max="100" :value.prop="uploadProgress"></progress> -->
<!--       Uploading: {{ uploadProgress }}% -->
<!--     </div> -->
<!--     <div v-if="uploadSuccess">Successfully uploaded files.</div> -->
<!--     <div v-if="extractedText"> -->
<!--       <h3>Extracted Text:</h3> -->
<!--       <pre>{{ extractedText }}</pre> -->
<!--     </div> -->
<!--   </div> -->
<!-- </template> -->

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
      <el-progress
        v-if="uploading"
        :percentage="uploadProgress"
        status="success"
      ></el-progress>
      <el-alert
        v-if="uploadSuccess"
        title="Files uploaded successfully."
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
    };
  },
  methods: {
    handleDragOver(e) {
      e.dataTransfer.dropEffect = "move";
    },
    handleDrop(e) {
      const files = e.dataTransfer.files;
      this.uploadFiles(files);
    },
    handleFileUpload(e) {
      const files = e.target.files;
      this.uploadFiles(files);
      this.$refs.fileInput.value = null;
    },
    openFileExplorer() {
      this.$refs.fileInput.click();
    },
    updateProcessingDots() {
      this.processingDots = ".".repeat((this.processingDots.length % 3) + 1);
    },
    async uploadFiles(file) {
      this.uploading = true;
      this.uploadProgress = 0;
      this.uploadSuccess = false;

      const formData = new FormData();
      formData.append("file", file.raw);

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

        const file_path = data.file_path;

        let processingTimer = setInterval(this.updateProcessingDots, 500);

        const response = await axios.get("http://localhost:5000/process", {
          params: {
            file_path: file_path,
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
/* .dots { */
/*   animation: blink 1s linear infinite; */
/* } */
/* @keyframes blink { */
/*   0% { */
/*     opacity: 1; */
/*   } */
/*   50% { */
/*     opacity: 0; */
/*   } */
/*   100% { */
/*     opacity: 1; */
/*   } */
/* } */
/* .drop-zone { */
/*   border: 2px dashed #ccc; */
/*   border-radius: 5px; */
/*   padding: 50px; */
/*   text-align: center; */
/*   cursor: pointer; */
/* } */
/* .drop-zone:hover { */
/*   background-color: #eee; */
/* } */
</style>
