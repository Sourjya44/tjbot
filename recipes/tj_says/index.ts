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

// read recipe-specific config
const config = TJBot.getRecipeConfig();

// get the list of actions that TJBot will ask you to do
const actions = config.actions;
const tjDidntSayLikelihood = Number(config.tjDidntSayLikelihood) ?? 0.33; // default to 33% of the time TJBot doesn't say "TJ Says"

if (!actions || !Array.isArray(actions) || actions.length === 0) {
    throw new Error('No actions defined. Please define some actions in recipe.toml.');
}

// instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: {
        led: true,
        microphone: true,
        servo: true,
        speaker: true,
    }
});

// gracefully handle Ctrl-C
process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

// ready!
console.log('===========');
console.log('  TJ SAYS  ');
console.log('===========');

console.log("Let's play TJ Says!");
console.log();
console.log("Press Ctrl-C to exit this recipe.");

// gracefully handle Ctrl-C
process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

const instructions = `
Let's play TJ Says! It's just like Simon Says! I will call out an action and you have to do it.
But pay close attention. If I don't say 'TJ Says' first, then don't do what I say!
Ready? Let's begin!
`

// speak the instructions
await tj.speak(instructions);

// now play the game :)
var lastActionIdx = -1;
var turnCounter = 0;
while (true) {
    tj.shine('green');

    // pick a random action
    let randIdx;
    do {
        randIdx = Math.floor(Math.random() * actions.length);
    } while (randIdx === lastActionIdx);
    lastActionIdx = randIdx;

    const action = actions[randIdx];

    // should we say "TJ Says"? only do this after the 3rd turn to give players a chance to warm up
    var sayTJ;
    if (turnCounter < 3) {
        sayTJ = true;
    } else {
        sayTJ = Math.random() > tjDidntSayLikelihood;
    }

    const message = sayTJ ? `T J says ${action}` : action;

    // speak the action
    await tj.speak(message);

    // wait a bit...
    await tj.pulse('orange');
    await tj.pulse('orange');
    await tj.pulse('orange');

    if (!sayTJ) {
        await tj.lowerArm();
        await tj.speak(`Did you ${action}? TJBot didn't say!`);
        await tj.raiseArm();
        await tj.sleep(1);
        await tj.speak("Let's play again!");
    }

    // increment the turn counter
    turnCounter = turnCounter + 1;
}
