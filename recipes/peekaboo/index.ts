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

const tj = await TJBot.getInstance().initialize({
    hardware: {
        camera: true,
        led: true,
        speaker: true,
        servo: true,
    }
});

const FACE_POLL_INTERVAL_MS = 150;
const SEARCH_REMINDER_INTERVAL_MS = 5000;
const LED_PULSE_INTERVAL_MS = 1000;

enum GameState {
    WAITING_TO_START = 'WAITING_TO_START',
    PLAYER_HIDES = 'PLAYER_HIDES',
    SEARCHING = 'SEARCHING',
    FACE_FOUND = 'FACE_FOUND',
    WAITING_FOR_NEXT_ROUND = 'WAITING_FOR_NEXT_ROUND',
}

const SEARCHING_REMINDERS = [
    "I don't see you, where did you go?",
    'Where are you hiding?',
    'I am still looking for you.',
    'I cannot find you yet.',
    'Are you still there? I don\'t see you!',
    'Peekaboo player, where did you go?',
];

let running = true;

const randomItem = (values: string[]): string => {
    const index = Math.floor(Math.random() * values.length);
    return values[index] ?? values[0];
};

type WaitForFaceOptions = {
    pulseColor?: string;
    reminderIntervalMs?: number;
    reminderPhrases?: string[];
};

const waitForFacePresence = async (
    targetPresent: boolean,
    options: WaitForFaceOptions = {}
): Promise<void> => {
    let nextPulseAt = Date.now();
    let nextReminderAt = Date.now() + (options.reminderIntervalMs ?? SEARCH_REMINDER_INTERVAL_MS);

    while (running) {
        const now = Date.now();

        if (options.pulseColor && now >= nextPulseAt) {
            nextPulseAt = now + LED_PULSE_INTERVAL_MS;
            await tj.pulse(options.pulseColor);
        }

        if (
            options.reminderIntervalMs &&
            options.reminderPhrases &&
            options.reminderPhrases.length > 0 &&
            now >= nextReminderAt
        ) {
            nextReminderAt = now + options.reminderIntervalMs;
            const reminder = randomItem(options.reminderPhrases);
            await tj.speak(reminder);
        }

        const imagePath = await tj.look();
        const result = await tj.detectFaces(imagePath);

        if (result.isFaceDetected === targetPresent) {
            return;
        }

        await tj.sleep(FACE_POLL_INTERVAL_MS);
    }
};

const cleanup = async (): Promise<void> => {
    await tj.shine('off');
    await tj.raiseArm();
};

process.on('SIGINT', () => {
    if (!running) {
        return;
    }

    running = false;
    console.log('\nStopping peekaboo...');
});

const runPeekaboo = async (): Promise<void> => {
    let state: GameState = GameState.WAITING_TO_START;

    while (running) {
        switch (state) {
            case GameState.WAITING_TO_START:
                console.log('State: WAITING_TO_START (waiting for face to show)');
                await tj.raiseArm();
                await tj.speak("Let's play a game of peekaboo!");
                await tj.speak("Show me your face to begin.");
                await waitForFacePresence(true, {
                    pulseColor: 'yellow',
                });
                await tj.shine('green');
                await tj.speak("I see you!");
                await tj.speak("Let's begin the game.");
                await tj.speak("Hide your face!");
                state = GameState.PLAYER_HIDES;
                break;

            case GameState.PLAYER_HIDES:
                console.log('State: PLAYER_HIDES (waiting for face to disappear)');
                await waitForFacePresence(false);
                state = GameState.SEARCHING;
                break;

            case GameState.SEARCHING: {
                console.log('State: SEARCHING (looking for face)');
                await waitForFacePresence(true, {
                    pulseColor: 'yellow',
                    reminderIntervalMs: SEARCH_REMINDER_INTERVAL_MS,
                    reminderPhrases: SEARCHING_REMINDERS,
                });
                state = GameState.FACE_FOUND;
                break;
            }

            case GameState.FACE_FOUND:
                console.log('State: FACE_FOUND (face detected)');
                await tj.shine('green');
                await tj.lowerArm();
                await tj.speak('Peekaboo, I found you!');
                state = GameState.WAITING_FOR_NEXT_ROUND;
                break;

            case GameState.WAITING_FOR_NEXT_ROUND:
                console.log('State: WAITING_FOR_NEXT_ROUND (waiting for face to hide)');
                await tj.raiseArm();
                await tj.shine('orange');
                await tj.speak("Let's play again.");
                await tj.speak("Hide your face!");
                await waitForFacePresence(false);
                state = GameState.SEARCHING;
                break;
        }
    }
};

console.log('============');
console.log('  PEEKABOO  ');
console.log('============');

console.log("Let's play Peekaboo!");
console.log("Press Ctrl-C to exit this recipe.");

try {
    await runPeekaboo();
} finally {
    console.log('\nGoodbye!');
    await cleanup();
    process.exit(0);
}
