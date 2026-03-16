# TJ the Translator

> 💬 🌎 Speak another language with TJBot!

This recipe uses Google Cloud Translation together with TJBot's speech input and speech output to turn TJBot into a language translator.

## Requirements

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B+-cc342d)](https://www.raspberrypi.org/)
![LED](https://img.shields.io/badge/Hardware-LED-orange)
![Microphone](https://img.shields.io/badge/Hardware-Speaker-orange)
![Speaker](https://img.shields.io/badge/Hardware-Speaker-orange)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-yellow)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![Google Cloud Translate](https://img.shields.io/badge/Google%20Cloud-Translate-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/translate)

> [!CAUTION]
> We recommend a Raspberry Pi 4+ for local Speech-to-Text (STT) recognition and Text-to-Speech (TTS) synthesis. The recipe will work on other Raspberry Pi hardware using cloud-based STT & TTS backends.

## How It Works

This recipe demonstrates TJBot's speech-to-text capabilities by having it listen to your speech and then translate it to another language using [Google Cloud Translate](https://cloud.google.com/translate).

## Configure

> [!CAUTION]
> Make sure you have configured your Raspberry Pi for TJBot by following the [bootstrap instructions](https://github.com/tjbot-ce/tjbot/wiki/Bring-TJBot-to-Life).

To use this recipe, you need to create a free Google Cloud project. You will turn on the Cloud Translation API for that project, then download a special credentials file that lets TJBot use it.

> [!NOTE]
> Making a Google Cloud project is free. Google may ask you to add a payment method before you can turn on the API, but many small projects stay within the free trial or free usage limits.

### 1. Create a Google Cloud project

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account.
3. At the top of the page, click the project name box.
4. Click **New Project**.
5. Type a name like **tjbot-translator**.
6. Click **Create**.
7. Wait a moment, then make sure your new project is selected.

### 2. Turn on Cloud Translation for your project

1. Open the [Cloud Translation API page](https://console.cloud.google.com/apis/library/translate.googleapis.com).
2. Check that your new project is selected at the top of the page.
3. Click **Enable**.

### 3. Make a robot account for TJBot

1. Open the [Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts).
2. Make sure your TJBot project is still selected.
3. Click **Create Service Account**.
4. In the name box, type **tjbot-translator**.
5. Click **Create and Continue**.
6. If Google shows extra permission steps, keep clicking **Continue** or **Done** unless it clearly says something is required.
7. When you are finished, you should see your new service account in the list.

### 4. Download the credentials file

1. Click the new service account you just made.
2. Click the **Keys** tab.
3. Click **Add Key**.
4. Click **Create new key**.
5. Choose **JSON**.
6. Click **Create**.
7. A JSON file will download to your computer. This is your credentials file.

### 5. Put the file where TJBot can find it

Save the downloaded file to your TJBot, ensure it is named `google-credentials.json`, and put it in one of these places:

1. In the **recipes/tj_the_translator** folder. In this location, only the `tj_the_translator` recipe will have access to these credentials.
2. In **~/.tjbot**. In this location, any tjbot recipes will be able to use these credentials.

> [!WARNING]
> The credentials file is private. Do not share it with other people or post it online.

## Run

You can run this recipe using the `tjbot` command or you can run it manually using `mise`.

### Run using `tjbot run`

Open a Terminal and run the following command from anywhere on your system:

```sh
tjbot run hello_tjbot
```

> [!NOTE]
> `tjbot` invokes `mise` under the hood, which will automatically install any required software dependencies before running the recipe.

You should see the following output:

```sh
$ tjbot run tj_the_translator

> tj_the_translator@3.0.0 start
> tsx index.ts

TODO: ADD SAMPLE CONSOLE OUTPUT HERE
```

> [!IMPORTANT]
> The first time you run this script, your TJBot may download a Speech to Text model. This download may take a little time, please be patient!

### Run manually using `mise`

Open a Terminal, navigate to this recipe's directory, and run using `mise`.

```sh
cd ~/.tjbot/recipes/tj_the_translator
mise run start
```

## Customize

### Customization 1: Translate to a different language

Change the language TJBot translates into by editing `recipe.toml`:

```toml
language = 'french' # 🇫🇷
```

You may also specify a language code for languages that need a specific locale:

```toml
language = 'pt-BR' # 🇧🇷
```

> [!TIP]
> Check out `index.ts` for a full list of supported languages. Look for the line that defines `LANGUAGE_NAME_TO_CODE`.

### Customization 2: Translate from a language other than English

You can make TJBot translate from a language other than English by changing the language code on this line:

```ts
const sourceLanguageCode = 'en';
```

> [!WARNING]
The local speech-to-text model only supports spoken English. If you would like TJBot to be able to listen to you speak in another language, you will also need to use one of the cloud-based STT backends. For this recipe, we recommend using Google Speech to Text and configuring it with a model that understands the language you wish to speak.

## Troubleshoot

If you are having difficulties in making this recipe work, please see the [troubleshooting guide](https://github.com/tjbot-ce/tjbot/wiki/Troubleshooting-TJBot).

## Contribute

If you would like to contribute to TJBot, please see the [contributor's guide](https://github.com/tjbot-ce/tjbot/wiki/Contributing-to-TJBot).

## License

This project is licensed under Apache 2.0. Full license text is available in [LICENSE](../../LICENSE).
