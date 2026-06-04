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

import TJBot from 'tjbot';

console.log('====================');
console.log('  WHAT DO YOU SEE?  ');
console.log('====================');

console.log('TJBot is ready to play!');
console.log(`Ask me what I see by saying "what do you see" and I will let you know!`);
console.log("Say 'stop' or press Ctrl-C to exit this recipe.");

// instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: {
        camera: true,
        led: true,
        microphone: true,
        speaker: true,
    },
});

process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

const exampleObjectIdeas = [
    'a toy car',
    'a teddy bear',
    'a soccer ball',
    'a water bottle',
    'a banana',
    'a book',
    'a backpack',
    'a shoe',
    'a hat',
    'a pencil',
    'a spoon',
    'a pair of sunglasses',
];

function pickRandomExamples<T>(items: T[], count: number): T[] {
    const shuffled = [...items];

    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }

    return shuffled.slice(0, Math.min(count, shuffled.length));
}

const [example1, example2, example3] = pickRandomExamples(exampleObjectIdeas, 3);

const instructions = `Hey, let's play a game! It's called "What Do You See?"
Your job is to find a cool object, like ${example1}, ${example2}, or ${example3},
or anything else you find interesting and show it to me. Then ask me,
"what do you see?" and I'll do my best to figure out what it is.
Ready? Let's play!`;
await tj.speak(instructions);

const objectCounts = new Map<string, number>();

function toOrdinal(n: number): string {
    const ordinalsUnderTen: Record<number, string> = {
        1: 'first',
        2: 'second',
        3: 'third',
        4: 'fourth',
        5: 'fifth',
        6: 'sixth',
        7: 'seventh',
        8: 'eighth',
        9: 'ninth',
        10: 'tenth',
    };

    if (ordinalsUnderTen[n]) {
        return ordinalsUnderTen[n];
    }

    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return `${n}st`;
    if (mod10 === 2 && mod100 !== 12) return `${n}nd`;
    if (mod10 === 3 && mod100 !== 13) return `${n}rd`;
    return `${n}th`;
}

function getIndefiniteArticle(phrase: string): 'a' | 'an' {
    const word = phrase.trim().toLowerCase();

    if (word.length === 0) {
        return 'a';
    }

    // Common silent-h words use "an".
    if (/^(honest|hour|honor|heir)/.test(word)) {
        return 'an';
    }

    // Some vowel-leading words sound like they start with "you" or "w".
    if (/^(university|unicorn|european|eucalyptus|one\b)/.test(word)) {
        return 'a';
    }

    return /^[aeiou]/.test(word) ? 'an' : 'a';
}

while (true) {
    console.log('👂 Listening...');
    await tj.shine('orange');

    let msg = await tj.listen();

    if (msg === undefined || msg === '') {
        console.log('No speech detected, trying again...');
        continue;
    }

    if (msg.toLowerCase().startsWith('stop')) {
        console.log('Goodbye!');
        process.exit(0);
    }

    if (msg.toLowerCase().includes('what do you see')) {
        await tj.shine('yellow');
        await tj.speak(`Let me take a look!`);
        const image = await tj.see();
        const objects = await tj.detectObjects(image);

        if (objects.length === 0) {
            await tj.speak(`Hmm, I don't see anything interesting. Can you show me something else?`);
        } else {
            // print out a list of seen objects to the console
            console.log('I see the following objects:');
            objects.forEach((obj) => {
                console.log(`- ${obj.label} (confidence: ${(obj.confidence * 100).toFixed(2)}%)`);
            });

            // choose a random object to focus on (since there are likely multiple)
            const randomIndex = Math.floor(Math.random() * objects.length);
            const obj = objects[randomIndex];
            const labelKey = obj.label.toLowerCase();
            const newCount = (objectCounts.get(labelKey) ?? 0) + 1;
            objectCounts.set(labelKey, newCount);
            const article = getIndefiniteArticle(obj.label);

            console.log(`Focusing on: ${article} ${obj.label} (confidence: ${(obj.confidence * 100).toFixed(2)}%)`);

            // respond based on how many times we've seen this object before
            if (newCount === 1) {
                await tj.speak(`I see ${article} ${obj.label}! That's really cool!`);
            } else if (newCount > 10) {
                await tj.speak(
                    `Hey, I've seen ${article} ${obj.label} more than ten times already! Show me something new!`
                );
            } else {
                await tj.speak(
                    `I see ${article} ${obj.label} again! That's the ${toOrdinal(newCount)} time you've shown me this!`
                );
            }
        }
    } else {
        console.log(`You said: "${msg}". Try asking "what do you see?" to play the game!`);
    }
}
