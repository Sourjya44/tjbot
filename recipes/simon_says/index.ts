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
import AssistantV2 from 'ibm-watson/assistant/v2.js';

// read recipe-specific config
const config = TJBot.getRecipeConfig();

// create an instance of the watsonx Assistant service
const assistant = new AssistantV2({
    serviceName: 'assistant',
    version: '2024-08-25',
});

// instantiate our TJBot!
const tj = await TJBot.getInstance().initialize({
    hardware: {
        microphone: true,
        speaker: true,
        led: true
    }
});

// keep track of the session id for watsonx Assistant
const assistantId = config.assistantId as string;
const environmentId = config.environmentId as string;
const followLikelihood = config.followLikelihood as number;

if (!assistantId || assistantId.trim() === '') {
    throw new Error('assistantId is required. Please define it in recipe.toml.');
}
if (!environmentId || environmentId.trim() === '') {
    throw new Error('environmentId is required. Please define it in recipe.toml.');
}

let assistantSessionId: string | undefined = undefined;

async function converse(message: string) {
    // set up the session if needed
    if (assistantSessionId === undefined) {
        try {
            console.log('Creating new watsonx Assistant session...');
            const body = await assistant.createSession({
                assistantId: assistantId,
                environmentId: environmentId
            });
            console.log('Success!');
            assistantSessionId = body.result.session_id;
        } catch (err) {
            console.error('An error occurred while creating a session for watsonx Assistant. Please check that the environmentId is defined in recipe.toml.');
            throw err;
        }
    }

    // define the conversational turn
    const turn = {
        assistantId: assistantId,
        environmentId: environmentId,
        sessionId: assistantSessionId,
        input: {
            'message_type': 'text' as const,
            'text': message,
            'options': {
                'return_context': true
            }
        }
    };

    // send to Assistant service
    try {
        const body = await assistant.message(turn);
        console.log(`response from assistant.message(): ${JSON.stringify(body)}`);
        const { result } = body;

        // get the response from the generic output
        const response = result.output.generic || [];

        const responseText = (response[0] && 'text' in response[0] ? response[0].text : '') as string;
        const assistantResponse = {
            object: result.output,
            description: responseText,
            action: result.context?.skills?.['actions skill']?.skill_variables?.tj_action
        };
        console.log(`received response from assistant: ${JSON.stringify(responseText)}`);
        return assistantResponse;
    } catch (err) {
        console.error(`the watsonx Assistant service returned an error: ${err}`);
        throw err;
    }
}

async function followAction(action: string | undefined, response: { description: string }, utterance: string) {
    // figure out what action they asked us to do
    // check if a variable to control the bot was found
    let followed = false;
    if (action !== undefined) {
        switch (action) {
            case 'lower-arm':
                await tj.speak(response.description);
                tj.lowerArm();
                followed = true;
                break;
            case 'raise-arm':
                await tj.speak(response.description);
                tj.raiseArm();
                followed = true;
                break;
            case 'wave':
                await tj.speak(response.description);
                tj.wave();
                followed = true;
                break;
            case 'greeting':
                await tj.speak(response.description);
                tj.wave();
                followed = true;
                break;
            case 'shine':
                {
                    // colors to detect from the user utterance
                    const regex = /(aqua|red|green|white|blue|orange|yellow|violet|pink|on|off)/g;

                    if (utterance.match(regex)) {
                        const color = utterance.match(regex)![0];
                        console.log('color found! ', color);
                        await tj.speak(response.description);
                        tj.shine(color);
                        followed = true;
                    }
                }
                break;
            default:
                break;
        }
    }

    if (!followed) {
        await tj.speak("oh no, I wasn't able to understand your instruction! let's try again.");
    }
}

// ready!
console.log('==============');
console.log('  SIMON SAYS  ');
console.log('==============');
console.log("Let's play Simon Says!");
console.log();
console.log("Say 'stop' or press ctrl-c to exit this recipe.");

// gracefully handle Ctrl-C
process.on('SIGINT', () => {
    console.log('\nGoodbye!');
    process.exit(0);
});

const instructions = `
Let's play Simon Says! Tell me what to do and I will do my best to follow.
I can shine my light different colors, move my arm up and down, and repeat
things that you say. Don't forget to say "Simon Says"! When you want to stop
playing, just say "Stop".
`;

// speak the instructions
await tj.speak(instructions);

// now we play the game :)
while (true) {
    const msg = await tj.listen();

    if (msg === undefined || msg === '') {
        continue;
    }

    const msgLower = msg.toLowerCase();

    if (msgLower === 'stop') {
        console.log('Goodbye!');
        process.exit(0);
    }

    // send to the assistant service
    const response = await converse(msg);

    // check to see if they said "Simon Says"
    if (msgLower.startsWith('simon says')) {
        // they said "simon says" so lets try to follow it
        await followAction(response.action, response, msg);
    } else {
        // they didn't say "simon says", but we might still follow the instruction
        const rand = Math.random();
        if (rand > followLikelihood) {
            // follow it
            await followAction(response.action, response, msg);

            // and then end the game
            await tj.speak("oh no, you didn't say simon says! good game!");
        } else {
            // don't follow it, they didn't say simon says!
            await tj.speak("you didn't say simon says! let's keep going.");
        }
    }
}
