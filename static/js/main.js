function showNotification(message, isError = false) {
 const toast = document.getElementById('toastNotification');
 const messageElement = toast.querySelector('.toast-message');
 
 if (isError) {
     if (message.includes('4.5MB')) {
         message = "File size should not exceed 4.5MB";
     } else if (typeof message === 'string' && message.trim()) {
         message = message;
     } else {
         message = "An error occurred. Please try again.";
     }
 }

 messageElement.textContent = message;
 toast.classList.remove('show', 'error', 'success');
 
 if (isError) {
     toast.classList.add('error');
 } else {
     toast.classList.add('success');
 }
 
 // Force reflow
 void toast.offsetWidth;
 toast.classList.add('show');
 
 // Hide notification after delay
 setTimeout(() => {
     toast.classList.remove('show');
 }, 3000);
}

function resetForm(form) {
 form.reset();

 form.querySelectorAll('input[type="file"]').forEach(input => {
     const button = input.previousElementSibling;
     if (button) {
         button.textContent = 'Choose File';
     }
 });

 form.querySelectorAll('.file-count').forEach(counter => {
     counter.textContent = '';
 });
}

document.querySelectorAll('form').forEach(form => {
 form.addEventListener('submit', async function(e) {
     e.preventDefault();
     
     const fileInputs = form.querySelectorAll('input[type="file"]');
     let hasFiles = false;
     let totalSize = 0;

     fileInputs.forEach(input => {
         if (input.files && input.files.length > 0) {
             hasFiles = true;
             Array.from(input.files).forEach(file => {
                 totalSize += file.size;
             });
         }
     });

     if (!hasFiles) {
         showNotification('Please select file(s) to process', true);
         return;
     }

     if (totalSize > 4.5 * 1024 * 1024) {
         showNotification('File size should not exceed 4.5MB', true);
         return;
     }

     if (form.id === 'merge-form') {
         const mergeInput = form.querySelector('input[type="file"]');
         if (mergeInput.files.length < 2) {
             showNotification('Please select at least two PDF files to merge', true);
             return;
         }
     }

     const progressOverlay = document.getElementById('progressOverlay');
     const progressCircle = document.querySelector('.progress-ring-circle');
     const progressText = document.querySelector('.progress-text');
     const progressStatus = document.querySelector('.progress-status');
     const radius = progressCircle.r.baseVal.value;
     const circumference = radius * 2 * Math.PI;

     progressCircle.style.strokeDasharray = `${circumference} ${circumference}`;
     progressCircle.style.strokeDashoffset = circumference;

     function setProgress(percent) {
         const offset = circumference - (percent / 100 * circumference);
         progressCircle.style.strokeDashoffset = offset;
         progressText.textContent = `${Math.round(percent)}%`;
         
         if (percent >= 100) {
             setTimeout(() => {
                 progressOverlay.classList.add('complete');
                 progressStatus.textContent = 'Complete!';
             }, 200);
         }
     }

     try {
         const formData = new FormData(form);
         progressOverlay.classList.remove('complete');
         progressOverlay.classList.add('active');
         
         const xhr = new XMLHttpRequest();
         xhr.open('POST', form.action, true);
         xhr.responseType = 'blob';

         xhr.upload.onprogress = (event) => {
             if (event.lengthComputable) {
                 const percentComplete = (event.loaded / event.total) * 100;
                 setProgress(percentComplete);
             }
         };

         xhr.onload = function() {
             if (xhr.status === 200) {
                 const contentType = xhr.getResponseHeader('Content-Type');
                 
                 if (contentType && contentType.includes('application/json')) {
                     const reader = new FileReader();
                     reader.onload = function() {
                         try {
                             const response = JSON.parse(this.result);
                             progressOverlay.classList.remove('active', 'complete');
                             showNotification(response.error || 'Operation failed', true);
                         } catch (e) {
                             progressOverlay.classList.remove('active', 'complete');
                             showNotification('Processing failed', true);
                         }
                     };
                     reader.readAsText(xhr.response);
                 } else {
                     setProgress(100);
                     setTimeout(() => {
                         const blob = xhr.response;
                         const url = window.URL.createObjectURL(blob);
                         const a = document.createElement('a');
                         const contentDisposition = xhr.getResponseHeader('Content-Disposition');
                         let filename = 'download';
                         
                         if (contentDisposition) {
                             const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                             if (filenameMatch && filenameMatch[1]) {
                                 filename = filenameMatch[1].replace(/['"]/g, '');
                             }
                         }
                         
                         a.href = url;
                         a.download = filename;
                         document.body.appendChild(a);
                         a.click();
                         window.URL.revokeObjectURL(url);
                         a.remove();
                         
                         setTimeout(() => {
                             progressOverlay.classList.remove('active', 'complete');
                             resetForm(form);
                             showNotification('Operation completed successfully');
                         }, 500);
                     }, 1000);
                 }
             } else {
                 progressOverlay.classList.remove('active', 'complete');
                 showNotification('Processing failed', true);
             }
         };

         xhr.onerror = function() {
             progressOverlay.classList.remove('active', 'complete');
             showNotification('Network error occurred', true);
         };

         xhr.send(formData);

     } catch (error) {
         progressOverlay.classList.remove('active', 'complete');
         showNotification(error.message || 'An error occurred', true);
     }
 });
});

document.querySelectorAll('input[type="file"]').forEach(input => {
 input.addEventListener('change', function() {
     const button = this.previousElementSibling;
     const fileCount = this.files.length;
     button.textContent = fileCount > 0 ? `${fileCount} file(s) selected` : 'Choose';
 });
});

document.querySelectorAll('input[type="file"]').forEach(input => {
 input.addEventListener('change', (e) => {
     const maxSize = 4.5 * 1024 * 1024; 
     let totalSize = 0;

     if (input.files) {
         for (let file of input.files) {
             totalSize += file.size;
         }

         if (totalSize > maxSize) {
             input.value = ''; 
             showNotification('File size should not exceed 4.5MB', true);
             return false;
         }
     }
     return true;
 });
});