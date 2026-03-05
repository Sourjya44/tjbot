/**
 * Copyright 2024 IBM Corp. All Rights Reserved.
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
import readlineSync from 'readline-sync';

// Read recipe-specific config
const config = TJBot.loadRecipeConfig();

// These are the hardware capabilities that our TJ needs for this recipe
const hardware = [
    TJBot.Hardware.SPEAKER
];

// Instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: hardware
});

console.log('TJBot is ready to speak!');
console.log("Type 'stop' or press ctrl-c to exit this recipe.\n");
console.log();
console.log('Type your message in the prompt below to have TJBot speak it!');

// prompt the user for input and respond
while (true) {
    const message = readlineSync.question('💬: ');
    
    // If the user types 'stop', exit the loop and close the interface
    if (message.toLowerCase() === 'stop') {
        console.log('🤖: Goodbye!');
        await tj.speak('Goodbye!');
        break;
    }

    console.log(`🤖: ${message}`);
    await tj.speak(message);
}
