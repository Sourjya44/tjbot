/**
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

import TJBot from 'tjbot-ce';

// Instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: {
        microphone: true,
        speaker: true,
    },
});

console.log('================');
console.log('     PARROT     ');
console.log('================');

console.log('TJBot is listening and will repeat what it hears!');
console.log("Say 'stop' or press Ctrl-C to exit this recipe.");

// gracefully handle Ctrl-C
process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

// listen and repeat what was heard
while (true) {
    const utterance = await tj.listen();

    if (!utterance || utterance.trim() === '') {
        continue;
    }

    if (utterance.toLowerCase().startsWith('stop')) {
        console.log('Goodbye!');
        await tj.speak('Goodbye!');
        break;
    }

    console.log(`TJBot heard: ${utterance}`);
    await tj.speak(utterance);
}
