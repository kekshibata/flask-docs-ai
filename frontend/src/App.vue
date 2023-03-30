<template>
  <div id="app">
    <FileUploader />
  </div>
</template>

<script>
import FileUploader from "./components/FileUploader.vue";

export default {
  components: {
    FileUploader,
  },
};
</script>

<!-- <template> -->
<!--   <div id="app"> -->
<!--     <h1>Drag and Drop</h1> -->
<!--     <div class="container"> -->
<!--       <div class="drop-area" @drop="dropHandler" @dragover="dragOverHandler"> -->
<!--         <div class="drop-area__icon"> -->
<!--           <i class="fas fa-file-upload"></i> -->
<!--         </div> -->
<!--         <div class="drop-area__text">Drag and Drop your files here</div> -->
<!--       </div> -->
<!--     </div> -->
<!--   </div> -->
<!-- </template> -->
<!---->
<!-- <script> -->
<!---->
<!-- export default { -->
<!--   name: 'App', -->
<!--   methods: { -->
<!--     dropHandler(event) { -->
<!--       event.preventDefault(); -->
<!--       console.log(event.dataTransfer.files); -->
<!--     }, -->
<!--     dragOverHandler(event) { -->
<!--       event.preventDefault(); -->
<!--       // send the files to the server, code below -->
<!---->
<!--       // send the files to the server -->
<!--       const formData = new FormData(); -->
<!--       for (let i = 0; i < event.dataTransfer.files.length; i++) { -->
<!--         formData.append('files', event.dataTransfer.files[i]); -->
<!--       } -->
<!--       axios.post('http://localhost:5000/upload', formData, { -->
<!--         headers: { -->
<!--           'Content-Type': 'multipart/form-data' -->
<!--         } -->
<!--       }).then(res => { -->
<!--         console.log(res); -->
<!--       }).catch(err => { -->
<!--         console.log(err); -->
<!--       }) -->
<!--     } -->
<!--   } -->
<!-- } -->
<!-- </script> -->

<!-- <template> -->
<!--   <div id="app"> -->
<!--     <h1>Drag and Drop</h1> -->
<!--     <div class="container"> -->
<!--       <div class="drop-area" @drop="dropHandler" @dragover="dragOverHandler"> -->
<!--         <div class="drop-area__icon"> -->
<!--           <i class="fas fa-file-upload"></i> -->
<!--         </div> -->
<!--         <div class="drop-area__text">Drag and Drop your files here</div> -->
<!--       </div> -->
<!--     </div> -->
<!--   </div> -->
<!-- </template> -->
<!---->

<!-- <style> -->
<!-- #app { -->
<!--   font-family: "Avenir", Helvetica, Arial, sans-serif; -->
<!--   -webkit-font-smoothing: antialiased; -->
<!--   -moz-osx-font-smoothing: grayscale; -->
<!--   text-align: center; -->
<!--   color: #2c3e50; -->
<!--   margin-top: 60px; -->
<!-- } -->
<!-- .container { -->
<!--   width: 100%; -->
<!--   height: 100vh; -->
<!--   display: flex; -->
<!--   justify-content: center; -->
<!--   align-items: center; -->
<!-- } -->
<!-- .drop-area { -->
<!--   width: 400px; -->
<!--   height: 200px; -->
<!--   border: 2px dashed #ccc; -->
<!--   border-radius: 20px; -->
<!--   display: flex; -->
<!--   justify-content: center; -->
<!--   align-items: center; -->
<!--   flex-direction: column; -->
<!-- } -->
<!-- .drop-area__icon { -->
<!--   font-size: 3rem; -->
<!--   color: #ccc; -->
<!-- } -->
<!-- .drop-area__text { -->
<!--   font-size: 1.5rem; -->
<!--   color: #ccc; -->
<!-- } -->
<!-- </style> -->
