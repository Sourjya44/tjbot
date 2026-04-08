/**
 * Copyright 2016-2024 IBM Corp. All Rights Reserved.
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

// let's have a disco party!
function discoParty(tj: TJBot, colors: string[]) {
    // Customization 1: Change the duration and speed of the disco party
    const discoDuration = 5 * 1000; // 5 seconds
    const discoSpeed = 250; // change colors every 250ms

    for (let i = 0; i < discoDuration / discoSpeed; i += 1) {
        setTimeout(() => {
            const randIdx = Math.floor(Math.random() * colors.length);
            const randColor = colors[randIdx];
            tj.shine(randColor);
        }, i * discoSpeed);
    }
}

// instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: {
        led: true,
        microphone: true,
        speaker: true,
    }
});

// full list of colors that TJ recognizes, e.g. ['red', 'green', 'blue']
const tjColors = tj.shineColors();

// pick 5 random colors to show as examples
const randomColors = [...tjColors].sort(() => Math.random() - 0.5).slice(0, 5);

console.log('===============');
console.log('  DISCO PARTY  ');
console.log('===============');

console.log('TJBot is ready to shine!');
console.log(`I understand lots of colors! Here are a few: ${randomColors.join(', ')}`);
console.log("You can tell me to shine my light a different color by saying 'turn the light red' or 'change the light to green' or 'turn the light off'.");
console.log("You can also say 'disco party' to have a disco party!");
console.log("Say 'stop' or press Ctrl-C to exit this recipe.");

// gracefully handle Ctrl-C
process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

// listen for speech
while (true) {
    const msg = await tj.listen();

    if (msg === undefined || msg === '') {
        continue;
    }

    console.log(`Heard: "${msg}"`);

    if (msg.toLowerCase().startsWith('stop')) {
        console.log('Goodbye!');
        process.exit(0);
    }

    const containsTurn = msg.indexOf('turn') >= 0;
    const containsChange = msg.indexOf('change') >= 0;
    const containsSet = msg.indexOf('set') >= 0;
    const containsLight = msg.indexOf('the light') >= 0;
    const containsDisco = msg.indexOf('disco') >= 0;
    const containsParty = msg.indexOf('party') >= 0;

    if ((containsTurn || containsChange || containsSet) && containsLight) {
        // check for 'on' or 'off' first (exact word match)
        if (msg.indexOf('off') >= 0) {
            tj.shine('off');
        } else if (msg.indexOf('on') >= 0) {
            tj.shine('on');
        } else {
            // try to find a color name by checking words and multi-word combinations
            const words = msg.toLowerCase().split(/\s+/);
            let foundColor = false;

            // try progressively longer word combinations (to match multi-word colors like "dark red")
            for (let len = 2; len >= 1; len--) {
                for (let i = 0; i <= words.length - len; i++) {
                    const candidate = words.slice(i, i + len).join('');  // remove spaces
                    if (tjColors.includes(candidate)) {
                        tj.shine(candidate);
                        foundColor = true;
                        break;
                    }
                }
                if (foundColor) break;
            }

            if (!foundColor) {
                console.log("Sorry, I didn't recognize that color. Try one of these:", randomColors.join(', '));
            }
        }
    } else if (containsDisco || containsParty) {
        discoParty(tj, tjColors);
    }
}
