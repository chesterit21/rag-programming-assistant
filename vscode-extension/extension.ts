import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    console.log('Congratulations, your extension "sfcore-rag-assistant" is now active!');

    let disposable = vscode.commands.registerCommand('sfcore.start', () => {
        const panel = vscode.window.createWebviewPanel(
            'ragAssistant',
            'RAG Assistant',
            vscode.ViewColumn.Beside,
            {
                enableScripts: true,
                localResourceRoots: [] // No local resources needed for this simple example
            }
        );

        panel.webview.html = getWebviewContent();

        panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'askQuestion':
                        const { question, category } = message.payload;
                        
                        try {
                            const response = await axios.post('http://localhost:7860/query', {
                                question: question,
                                category: category || null
                            }, { responseType: 'stream' });

                            let buffer = '';
                            response.data.on('data', (chunk: Buffer) => {
                                buffer += chunk.toString();
                                let boundary = buffer.indexOf('\n');
                                while (boundary !== -1) {
                                    const jsonString = buffer.substring(0, boundary);
                                    buffer = buffer.substring(boundary + 1);
                                    if (jsonString) {
                                        try {
                                            const messageData = JSON.parse(jsonString);
                                            panel.webview.postMessage({ command: 'updateStream', payload: messageData });
                                        } catch (e) {
                                            console.error('Failed to parse JSON chunk:', jsonString, e);
                                        }
                                    }
                                    boundary = buffer.indexOf('\n');
                                }                            });

                        } catch (error) {
                            let errorMessage = 'Gagal menghubungi RAG API.';
                            if (axios.isAxiosError(error)) {
                                errorMessage += ` Detail: ${error.message}`;
                            }
                            vscode.window.showErrorMessage(errorMessage);
                            panel.webview.postMessage({ command: 'showError', text: errorMessage });
                            console.error(error);
                        }
                        return;
                    case 'showError':
                        vscode.window.showErrorMessage(message.text);
                        return;
                }
            },
            undefined,
            context.subscriptions
        );
    });

    context.subscriptions.push(disposable);
}

function getWebviewContent() {
    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RAG Assistant</title>
        <style>
            body { font-family: var(--vscode-font-family); color: var(--vscode-editor-foreground); background-color: var(--vscode-editor-background); }
            textarea, input { width: 95%; background-color: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); padding: 4px; margin-bottom: 8px; }
            button { border: 1px solid var(--vscode-button-border); background-color: var(--vscode-button-background); color: var(--vscode-button-foreground); padding: 4px 8px; cursor: pointer; }
            button:hover { background-color: var(--vscode-button-hover-background); }
            #answer { white-space: pre-wrap; background-color: var(--vscode-text-block-quote-background); border: 1px solid var(--vscode-text-block-quote-border); padding: 8px; margin-top: 10px; min-height: 100px; }
        </style>
    </head>
    <body>
        <h1>RAG Programming Assistant</h1>
        <label for="question">Pertanyaan:</label>
        <textarea id="question" rows="4"></textarea>
        <label for="category">Kategori (opsional):</label>
        <input type="text" id="category" placeholder="ddd, asp.netcore, ...">
        <button onclick="ask()">Ask</button>
        <hr>
        <h3>Jawaban:</h3>
        <div id="answer"></div>
        <script>
            const vscode = acquireVsCodeApi();
            const answerDiv = document.getElementById('answer');
            let isStreamingAnswer = false;

            function ask() {
                const question = document.getElementById('question').value;
                const category = document.getElementById('category').value;
                if (!question) { vscode.postMessage({ command: 'showError', text: 'Pertanyaan tidak boleh kosong.' }); return; }
                isStreamingAnswer = false; // Reset flag
                answerDiv.innerHTML = '';
                vscode.postMessage({ command: 'askQuestion', payload: { question, category } });
            }

            window.addEventListener('message', event => {
                const message = event.data;
                if (message.command === 'updateAnswer') {
                    const text = message.text;
                    if (text.startsWith('🔍') || text.startsWith('✍️')) {
                        answerDiv.innerHTML = text; // Display status message
                        isStreamingAnswer = false;
                    } else {
                        if (!isStreamingAnswer) {
                            answerDiv.innerHTML = text; // First chunk of the answer, replace status
                            isStreamingAnswer = true;
                        } else {
                            answerDiv.innerHTML += text; // Subsequent chunks, append
                        }
                    }
                } else if (message.command === 'showError') {
                    answerDiv.innerHTML = \`<span style="color: var(--vscode-error-foreground);">Error: \${message.text}</span>\`;
                }
            });
        </script>
    </body>
    </html>`;
}

export function deactivate() {}