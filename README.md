# Map Style of [Guru Maps](https://gurumaps.app)

Syntax of this file is based on MapCSS inspired [file format](https://gurumaps.app/docs/mapcss/), with some unique features and some limitations.

## How to use

To add this style into the app. Copy `Default.style` folder into the app Documents folder. It will be added into the offline maps list as `Default`. Feel free to change icons, colors and change the name to anything you want. It won't break map style included into the app. You can make multiple map styles for different tasks.

## Install to Guru Maps (macOS)

Use the VS Code task **"Install Style: Copy Default.style to Guru Maps"**
(Tasks → Run Task) or run the script directly:

```bash
./deploy_style.sh
```

It copies the `Default.style` folder to
`~/Library/Containers/com.bodunov.galileo/Data/Documents/Default.style`
(overwriting an existing installation).

## Contribute

We're open to pull requests. Don't hesitate.

## Links

* OS: https://apps.apple.com/us/app/guru-maps/id321745474
* Android: https://play.google.com/store/apps/details?id=com.bodunov.galileo
