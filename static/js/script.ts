const fileInput = document.querySelector('#file-input') as HTMLInputElement;
const submitButton = document.querySelector('#submit-button') as HTMLButtonElement;
const customFileLabel = document.querySelector('.custom-file-label') as HTMLLabelElement;
const analyzeButton = document.querySelector('#analyze-button') as HTMLButtonElement;
const spinID = document.querySelector("#spin-ID") as HTMLSpanElement;
const analyzeButtonText = document.querySelector("#analyze-text") as HTMLSpanElement;
const contentContainer = document.querySelector('#content-container') as HTMLDivElement;
const loadingIndicator = document.querySelector('#loading-indicator') as HTMLDivElement;

fileInput.addEventListener('change', function () {
    const file = this.files![0];
    if (file) {
        submitButton.disabled = !file.name.endsWith('.pdf');
        customFileLabel.textContent = file.name;
    }
});

analyzeButton.addEventListener('click', () => {
    analyzeButton.disabled = true;
    spinID.style.display = 'inline-block';
    analyzeButtonText.innerHTML = "Loading...";
    contentContainer.style.display = 'none';
    loadingIndicator.style.display = 'block';
    submitButton.disabled = true;
    spinID.hidden = false;
    fetch('/pdf-grid')
        .then(response => response.text())
        .then(data => {
            contentContainer.style.display = 'block';
            analyzeButton.disabled = false;
            spinID.style.display = 'none';
            analyzeButtonText.innerHTML = "Analyze";
            loadingIndicator.style.display = 'none';
            submitButton.disabled = false;
            analyzeButton.style.display = 'none';
            contentContainer.innerHTML = data;
            document.querySelectorAll('.pdf-item').forEach((item, index) => {
                const fileUrl = (item as HTMLDivElement).dataset.fileurl as string;
                const containerId = `pdf-container-${index}`;
                item.setAttribute('id', containerId);
                printPDF(fileUrl, containerId);
            });
        });
});

submitButton.addEventListener('click', (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', fileInput.files![0]);
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            fetch('/pdf_container')
                .then(response => response.text())
                .then(data => {
                    contentContainer.innerHTML = data;
                    fetch('/uploaded_file')
                        .then(response => response.text())
                        .then(data => {
                            analyzeButton.style.display = 'block';
                            const currentFileUrl = `/current_book/${data}`;
                            printPDF(currentFileUrl);
                        });
                });
        })
        .catch(error => {
            console.log('Error:', error.message);
        });
});


const printPDF = (fileUrl: string, containerId = 'pdf-container') => {
    // @ts-ignore
    const pdfjsLib = window['pdfjs-dist/build/pdf'];
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://mozilla.github.io/pdf.js/build/pdf.worker.js';

    const pdfContainer = document.getElementById(containerId) as HTMLDivElement;
    const canvasId = `the-canvas-${containerId}`;
    pdfContainer.innerHTML = `<canvas id="${canvasId}"></canvas>`;

    const loadingTask = pdfjsLib.getDocument(fileUrl);
    // @ts-ignore
    loadingTask.promise.then((pdf) => {
        const pageNumber = 1;
        // @ts-ignore
        pdf.getPage(pageNumber).then((page) => {

            const desiredWidth = containerId === 'pdf-container' ? page.getViewport({scale: 1}).width * 0.5 : 200;
            const originalWidth = page.getViewport({scale: 1}).width;
            const scale = desiredWidth / originalWidth;

            const viewport = page.getViewport({scale: scale});

            const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
            canvas.style.border = '1px solid black';
            canvas.style.cursor = 'pointer';
            canvas.addEventListener('click', () => {
                window.open(fileUrl, '_blank');
            });

            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            const renderTask = page.render(renderContext);
            renderTask.promise.then(() => {
            });
        });
    }, (reason: Error) => {
        console.error(reason);
    });
}

