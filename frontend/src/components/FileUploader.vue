<template>
  <div>
    <div
      @dragover.prevent="handleDragOver"
      @drop.prevent="handleDrop"
      @click="openFileExplorer"
      class="drop-zone"
    >
      クリックしてファイルを選択するか、ここにファイルをドロップしてください。
    </div>
    <input
      type="file"
      ref="fileInput"
      @change="handleFileUpload"
      style="display: none"
      multiple
    />
    <div v-if="uploading">
      <progress max="100" :value.prop="uploadProgress"></progress>
      Uploading: {{ uploadProgress }}%
    </div>
    <div v-if="uploadSuccess">Successfully uploaded files.</div>
    <div v-if="extractedText">
      <h3>Extracted Text:</h3>
      <pre>{{ extractedText }}</pre>
    </div>
  </div>
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
    async uploadFiles(files) {
      this.uploading = true;
      this.uploadProgress = 0;
      this.uploadSuccess = false;

      const formData = new FormData();
      for (const file of files) {
        formData.append("files", file);
      }

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
