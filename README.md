<div id="top"></div>

<div style="text-align: center;">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/BLovegrove/boomer">
    <img src="https://cdn.discordapp.com/app-icons/887606123782344704/d193530a914689ea03312cf0faca5521.png?size=100" style="border-radius:50%;" alt="Logo" width="100" height="100">
  </a>

<h3 align="center">Boomer - A Python-based Discord Music Bot</h3>

  <p align="center">
    Boomer plays music.
    <br /><br />
    His name was something of a play on the word 'boombox' , and the idea behind him was to make a small, expandable, useful discord music bot for a private group of lovable nerds called the Lusty Argonian Maidz (Please don't ask about the name).
    <br /><br />
    I made the bot by learning from those that were destroyed before it (Rythm, Groovy, etc. - thanks for your service folks).
    <!-- <br />
    <a href="https://github.com/BLovegrove/boomer"><strong>Explore the docs »</strong></a> -->
    <br />
    <br />
    <!-- <a href="https://github.com/BLovegrove/boomer">View Demo</a>
    · -->
    <a href="https://github.com/BLovegrove/boomer/issues">Report Bug</a>
    ·
    <a href="https://github.com/BLovegrove/boomer/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <!-- <li><a href="#usage">Usage</a></li> -->
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <!-- <li><a href="#acknowledgments">Acknowledgments</a></li> -->
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<img src="https://raw.githubusercontent.com/BLovegrove/boomer/main/images/boomer-profile.png" style="border-radius: 10px;"><br />

Boomer is entirely developed by me using the libraries and technologies listed in <a href="#built-with">Built With</a>. 

Because my server only needed the music functionality, that's what he's limited for now - but 
more features or enhancements would be welcome! See <a href="#contributing">Contributing</a> for more info on that. 

Boomer also has a miniscule memory/computing footprint. I've been running him at home with a Raspberry Pi on 2GB of RAM and still managing to squeeze almost 20 instances playing at once out of him in testing (with wiggle-room to spare).

The CPU usage is so low it barely registers above 5% on the Pi's ARM processor at 700-800 MHz.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [LavaLink](https://github.com/freyacodes/Lavalink)
* [SpotiPy](https://github.com/plamere/spotipy)
* [Pandas](https://pandas.pydata.org/)
* [Discord.py](https://github.com/Rapptz/discord.py)


<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started


To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* Compatable [LavaLink](https://github.com/freyacodes/Lavalink) and accompanying java version)
* [Python 3.8](https://www.python.org/downloads/release/python-380/)
* Python3 [PIP](https://pypi.org/project/pip/) and [Pipenv](https://pipenv.pypa.io/en/latest/) for the dependencies found in the [Pipfile](https://github.com/BLovegrove/boomer/blob/7c00960a6e7b4342bea0e563b387c384002f8881/Pipfile)

### Installation

1. Create a free app for your SpotiPY [API key](https://developer.spotify.com/dashboard/)
2. Create a [Discord Bot](https://discord.com/developers/applications)
3. Clone the repo
   ```sh
   git clone https://github.com/BLovegrove/boomer.git
   ```
4. Create pipenv with dependencies
   ```python
   pipenv install
   ```
5. Rename [config-template](https://github.com/BLovegrove/boomer/blob/7c00960a6e7b4342bea0e563b387c384002f8881/config-template.toml) and [application-template](https://github.com/BLovegrove/boomer/blob/7c00960a6e7b4342bea0e563b387c384002f8881/application-template.yaml) to config.toml and application.yml respectively
7. Fill out `password` in [application.yaml](https://github.com/BLovegrove/boomer/blob/7c00960a6e7b4342bea0e563b387c384002f8881/application-template.yaml)

8. Fill out `guild_ids`, `owner_id`, bot `token & id`, `idle_track`, `pwd`, and Spotify `id & secret` in [config.toml](https://github.com/BLovegrove/boomer/blob/7c00960a6e7b4342bea0e563b387c384002f8881/config-template.toml)
(pwd field is the same as the password field in your [application.yaml](https://github.com/BLovegrove/boomer/blob/7c00960a6e7b4342bea0e563b387c384002f8881/application-template.yaml))
9. Launch LavaLink jar and wait for it to boot.
    ```sh
    java -jar <lavalink jar path>
    ```
10. Launch bot and wait for '<bot name#number> connected'.
    ```sh
    python -m bot
    ```



<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [x] ~~Paged list for the queue~~
- [x] ~~Spotify and Soundcloud search integration~~
- [x] ~~Idle music when nothing is playing~~
- [x] ~~'Now Playing' song info~~
- [x] ~~Differentiate skipping whole queue to a point, or jumping that one song to the front of the queue~~
- [x] ~~Join queue without playing anything~~
- [ ] User - by - user favorites list
- [ ] Report command to send owner of the bot instance a discord message with a copy of the log and a warning that something went wrong.


See the [open issues](https://github.com/BLovegrove/boomer/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Brandon Lovegrove - [@B_A_Lovegrove](https://twitter.com/B_A_Lovegrove) - b.lovegrove.wsd@gmail.com

Project Link: [https://github.com/BLovegrove/boomer](https://github.com/BLovegrove/boomer)

<br />

Like my work?

<a href="https://www.buymeacoffee.com/blovegrove" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60px" width="217px" ></a>

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/BLovegrove/boomer.svg?style=for-the-badge
[contributors-url]: https://github.com/BLovegrove/boomer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BLovegrove/boomer.svg?style=for-the-badge
[forks-url]: https://github.com/BLovegrove/boomer/network/members
[stars-shield]: https://img.shields.io/github/stars/BLovegrove/boomer.svg?style=for-the-badge
[stars-url]: https://github.com/BLovegrove/boomer/stargazers
[issues-shield]: https://img.shields.io/github/issues/BLovegrove/boomer.svg?style=for-the-badge
[issues-url]: https://github.com/BLovegrove/boomer/issues
[license-shield]: https://img.shields.io/github/license/BLovegrove/boomer.svg?style=for-the-badge
[license-url]: https://github.com/BLovegrove/boomer/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: linkedin.com/in/brandon-lovegrove-5ab4181a0
[product-screenshot]: images/screenshot.png
