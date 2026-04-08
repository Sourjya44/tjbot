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
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { TranslationServiceClient } from '@google-cloud/translate';

const LANGUAGE_NAME_TO_CODE: Record<string, string> = {
    arabic: 'ar',
    chinese: 'zh-CN',
    czech: 'cs',
    danish: 'da',
    dutch: 'nl',
    english: 'en',
    finnish: 'fi',
    french: 'fr',
    german: 'de',
    greek: 'el',
    hebrew: 'he',
    hindi: 'hi',
    hungarian: 'hu',
    indonesian: 'id',
    italian: 'it',
    japanese: 'ja',
    korean: 'ko',
    norwegian: 'no',
    polish: 'pl',
    portuguese: 'pt',
    romanian: 'ro',
    russian: 'ru',
    slovak: 'sk',
    spanish: 'es',
    swedish: 'sv',
    thai: 'th',
    'traditional chinese': 'zh-TW',
    turkish: 'tr',
    ukrainian: 'uk',
    vietnamese: 'vi',
};

function resolveLanguageCode(language: string): string {
    const normalized = language.trim().toLowerCase();

    if (/^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/i.test(normalized)) {
        return normalized; // already in a valid Google Cloud language code format
    }

    const mapped = LANGUAGE_NAME_TO_CODE[normalized];
    if (mapped) {
        return mapped;
    }

    throw new Error(`Unsupported language "${language}". Please use a supported language name like "es" or "japanese".`);
}

function findGoogleCredentialsPath(): string | undefined {
    const candidates = [
        path.join(process.cwd(), 'google-credentials.json'),
        path.join(os.homedir(), '.tjbot', 'google-credentials.json'),
    ];

    for (const candidate of candidates) {
        if (fs.existsSync(candidate)) {
            return candidate;
        }
    }

    return undefined;
}

// read recipe-specific config
const config = TJBot.getRecipeConfig();
if (typeof config.language !== 'string' || config.language.trim() === '') {
    throw new Error('language is required. Please define it in recipe.toml.');
}

const targetLanguageLabel = config.language.trim();
const sourceLanguageCode = 'en';
const targetLanguageCode = resolveLanguageCode(targetLanguageLabel);
const googleCredentialsPath = findGoogleCredentialsPath();

const translationClient = new TranslationServiceClient(
    googleCredentialsPath
        ? { keyFilename: googleCredentialsPath }
        : {},
);
const googleProjectId = await translationClient.getProjectId();

async function translateText(text: string): Promise<string> {
    const [response] = await translationClient.translateText({
        parent: `projects/${googleProjectId}/locations/global`,
        contents: [text],
        mimeType: 'text/plain',
        sourceLanguageCode,
        targetLanguageCode,
    });

    const translatedText = response.translations?.[0]?.translatedText?.trim();
    if (!translatedText) {
        throw new Error('Google Cloud Translation returned an empty result.');
    }

    return translatedText;
}

// instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    log: {
        level: 'verbose',
    },
    hardware: {
        led: true,
        microphone: true,
        speaker: true,
    }
});

// ready!
console.log("=====================");
console.log("  TJ THE TRANSLATOR  ");
console.log("=====================");

console.log('TJBot is ready for translation!');
console.log("Say 'stop' or press Ctrl-C to exit this recipe.");

process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

const instructions = `Hello! I'm T J Bot and I will be your language translator.
Please say something in English and I will translate it to ${targetLanguageLabel}!`;
await tj.speak(instructions);

while (true) {
    console.log('👂 Listening...');
    await tj.shine('orange');

    const msg = await tj.listen();

    if (msg === undefined || msg === '') {
        console.log('No speech detected, trying again...');
        continue;
    }

    if (msg.toLowerCase() === 'stop') {
        console.log('Goodbye!');
        process.exit(0);
    }

    // translate it
    try {
        await tj.pulse('orange');
        console.log(`👩‍💻 > ${msg}`);
        const translatedText = await translateText(msg);
        console.log(`🌐 > ${translatedText}`);

        await tj.speak(translatedText);
    } catch (err) {
        const errorMessage = err instanceof Error ? err.message : String(err);
        console.warn(`⚠️ Translation failed: ${errorMessage}`);
        await tj.speak(`Sorry, I couldn't translate that to ${targetLanguageLabel}.`);
    }
}
