/**
 * Copyright 2024-2025 IBM Corp. All Rights Reserved.
 * Copyright 2026-present TJBot Contributors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import TJBot from 'tjbot';
import { WatsonXAI } from '@ibm-cloud/watsonx-ai';
import { IamAuthenticator } from 'ibm-cloud-sdk-core';
import { inspect } from 'node:util';

const BASE_PROMPT = `
You are TJBot, a friendly and helpful social robot made out of cardboard.
You are having a conversation with a human.
You provide friendly and helpful responses to everything the human says.
You respond to their questions in a professional manner.
You never use inappropriate language like swear words or hate speech.
You aim to be delightful and energetic in your responses.
If you don't know the answer to a question, you respond truthfully that you do not know.
`;

// read recipe-specific config
const config = TJBot.getRecipeConfig();

// create an instance of the watsonx.ai service
const wxai = WatsonXAI.newInstance({
    authenticator: new IamAuthenticator({ apikey: config.apiKey as string }),
    serviceUrl: config.serviceUrl as string | undefined,
    version: config.serviceVersion as string | undefined,
});

// keep track of the conversational history
let conversationHistory = '';

// instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: {
        led: true,
        microphone: true,
        speaker: true
    }
});

// ready!
console.log('================');
console.log('  CHAT WITH TJ  ');
console.log('================');

console.log('TJBot is ready for conversation!');
console.log("Say 'stop' or press Ctrl-C to exit this recipe.");

// gracefully handle Ctrl-C
process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

while (true) {
    console.log('👂 listening...');

    tj.shine('green');
    let msg = await tj.listen();
    tj.pulse('orange');

    if (msg === undefined || msg === '') {
        continue;
    }

    if (msg.toLowerCase().startsWith('stop')) {
        console.log('Goodbye!');
        process.exit(0);
    }

    // strip out %HESITATION
    msg = msg.replaceAll('%HESITATION', '');

    // build the prompt
    const prompt = `
${BASE_PROMPT}

Conversation summary:
${conversationHistory}

Conversation:

H: ${msg}
AI: `;

    const params = {
        input: prompt,
        modelId: config.modelId as string,
        projectId: config.projectId as string,
        parameters: {
            decoding_method: (config.modelDecodingMethod as string) || 'greedy',
            temperature: (config.modelTemperature as number) || 0.7,
            random_seed: (config.modelRandomSeed as number) || 42,
            min_new_tokens: (config.modelMinNewTokens as number) || 0,
            max_new_tokens: (config.modelMaxNewTokens as number) || 200,
            stop_sequences: ['.'],
            repetition_penalty: (config.modelRepetitionPenalty as number) || 1.0,
        },
    };

    try {
        const response = await wxai.generateText(params);
        const text = response.result.results[0].generated_text.split(/\r?\n/, 1)[0];

        console.log(`👩‍💻 ${msg}`);
        console.log(`🤖 ${text}`);

        console.log('🗯️ speaking...');
        tj.pulse('yellow');

        await tj.speak(text);
        console.log('🗯️ speaking finished');

        // add to the conversation history
        conversationHistory += `Human: ${msg}\n AI: ${text}\n\n`;
    } catch (err: unknown) {
        console.warn(`⚠️ watsonx.ai request failed: ${inspect(err, { depth: null })}`);
    }
}
