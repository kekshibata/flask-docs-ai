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
          Only PDF files are supported.
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
    async uploadFiles(file) {
      this.uploading = true;
      this.uploadProgress = 0;
      this.uploadSuccess = false;

      const formData = new FormData();
      formData.append("file", file.raw);

      try {
        const response = await axios.post(
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

        if (response.status === 200) {
          this.uploadSuccess = true;
          console.log(response.data);
          if (response.data.content) {
            this.extractedText = response.data.content;
          }
        }
      } catch (error) {
        console.error("Upload failed:", error);
      } finally {
        this.uploading = false;
      }
    },
  },
};
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 5px;
  padding: 50px;
  text-align: center;
  cursor: pointer;
}
.drop-zone:hover {
  background-color: #eee;
}
</style>
