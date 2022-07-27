import { EmbedBuilder } from "@discordjs/builders";
import { Player, PlaylistInfo, SearchResult, Track, TrackUtils, UnresolvedTrack } from "erela.js";
import config from "../../config.json"
import truncate from "truncate";
import { CommandInteraction, GuildMember } from "discord.js";
import ProgressBar from "string-progressbar";
import timeFormat from "format-duration";
import { APIEmbed } from "discord-api-types/v9";

export class TrackEmbedBuilder {
    data: APIEmbed
    sender: GuildMember

    /**
     * creates an embed builder pre-loaded with data to display the current song info.
     * complete with song requester, author details, and music video thumbnails.
     * @param interaction Discord.js command interaction for loading the requested track
     * @param track track data for the requested song
     * @param player erela.js player
     */
    constructor(interaction: CommandInteraction, track: Track | UnresolvedTrack, player: Player) {

        this.sender = interaction.member as GuildMember

        this.data = {
            color: config.server.embedColor,
            description: `Song by: ${track.author}`,
            author: {
                name: `Song queued by ${this.sender.displayName}: `,
                url: track.uri,
                icon_url: this.sender.avatarURL() as string
            }
        }

        if (TrackUtils.isTrack(track)) {
            this.data.thumbnail = {
                url: `https://i.ytimg.com/vi/${track.identifier}/mqdefault.jpg`
            }

        } else {
            this.data.thumbnail = {
                url: "https://i.imgur.com/hpjK2ym.png"
            }
        }

        if (!player.playing || player.get('idle')) {
            this.data.title = `Now playing: ${track.title}`
        } else {
            this.data.title = track.title
            this.data.footer = {
                text: `Song is #${player.queue.length + 1} in queue`
            }
        }
    }

    toJSON() {
        return new EmbedBuilder(this.data).toJSON()
    }
}

/**
     * creates an embed builder pre-loaded with data to display the recently removed track.
     * complete with custom message indicating who removed the track.
     * @param interaction Discord.js command interaction for clearig the track
     * @param track track removed from the queue
     * @param player erela.ks player
     */
export class ClearedEmbedBuilder extends TrackEmbedBuilder {
    
    constructor(interaction: CommandInteraction, track: Track | UnresolvedTrack, player: Player) {
        super(interaction, track, player)

        if (!track) {
            return
        }

        this.data.author!.name = `${this.sender.displayName} cleared a song from queue:`
    }
}

export class SkipEmbedBuilder extends TrackEmbedBuilder {
    
    /**
     * creates an embed builder pre-loaded with data to display the current song info.
     * complete with track skipper and next song details.
     * @param interaction Discord.js command interaction for loading the next track
     * @param track first track in queue taken before skip executes
     * @param player erela.ks player
     * @param index place in queue thats being skipped to
     */
    constructor(interaction: CommandInteraction, track: Track | UnresolvedTrack, player: Player, index: number) {
        super(interaction, track, player)

        if (!track) {
            return
        }

        this.data.author!.name = `Track skipped by ${this.sender.displayName}`
        this.data.title = `Now playing: ${track.title}`
        this.data.footer!.text = `${player.queue.length - 1} tracks left in queue.`
    }
}

export class ProgressEmbedBuilder extends TrackEmbedBuilder {

    /**
     * creates an embed builder pre-loaded with data to display the current song info.
     * complete with song details and progress bar.
     * @param interaction Discord.js command interaction for loading the progress data
     * @param player erela.js player
     */
    constructor(interaction: CommandInteraction, player: Player) {

        var currentTrack = player.queue.current as Track

        super(interaction, currentTrack, player)

        if (!currentTrack) {
            return
        }

        const durationTotal = player.queue.current!.duration as number
        const durationCurrent = player.position
        const progress = ProgressBar.filledBar(
            durationTotal,
            durationCurrent,
            20
        ).toString()

        this.data.author!.name = `Info requested by: ${this.sender.displayName}`
        this.data.footer!.text = `🎵 ${timeFormat(durationCurrent, { leading: true })} ${progress} ${timeFormat(durationTotal, { leading: true })} 🎵`
    }
}

export class PlaylistEmbedBuilder {
    data: APIEmbed
    sender: GuildMember

    /**
     * creates an embed builder pre-loaded with data to display the playlist you just enqueued.
     * complete with playlist name, queue position umbers, and current song data.
     * @param interaction Discord.js command interaction for loading the playlist
     * @param result entire erela.js player search result
     * @param player erela.js player
     */
    constructor(interaction: CommandInteraction, result: SearchResult, player: Player) {

        this.sender = interaction.member as GuildMember
        const tracks = result.tracks
        const playlist = result.playlist as PlaylistInfo

        this.data = {
            color: config.server.embedColor,
            description: `:notepad_spiral: Playlist: ${playlist.name}`,
            author: {
                name: `Playlist queued by ${this.sender.displayName}`,
                url: "https://tinyurl.com/boomermusic",
                icon_url: this.sender.avatarURL() as string
            },
            thumbnail: {
                url: `https://i.ytimg.com/vi/${tracks.at(0)!.identifier}/mqdefault.jpg`
            }
        }

        if (!player.playing || player.get('idle')) {
            this.data.title = `Now playing: ${tracks.at(0)!.title}`
            this.data.footer = {
                text: `Remaining songs are #1 to #${tracks.length - 1} in queue.`
            }
        } else {
            this.data.title = `Added ${tracks.at(0)!.title} and ${tracks.length - 1} more to queue`
            this.data.footer = {
                text: `Songs are #${player.queue.length} to #${player.queue.length + tracks.length} in queue.`
            }
        }

    }

    toJSON() {
        return new EmbedBuilder(this.data).toJSON()
    }
}

export class ListEmbedBuilder {
    data: APIEmbed

    /**
     * creates an embed builder pre-loaded with data to display the queue one page at a time.
     * complete with active modifiers, page numbers, queue positions, and current song data.
     * @param player erela.js player
     * @param page number of the page to generate an embed for
     */
    constructor(player: Player, page: number) {

        const listStart = (page - 1) * config.music.listPageLength
        const listEnd = (
            page < player.get<number>('pages')
            ? listStart + (config.music.listPageLength - 1) 
            : player.queue.length - 1
        )

        const track = player.queue.current as Track

        var modifiers = (
            player.trackRepeat ? ":repeat_one:" : "" + 
            player.queueRepeat ? ":repeat:" : ""
            // TODO: Shuffle :((
        )

        this.data = {
            color: config.server.embedColor,
            title: `Now playing: ***${track.title}***`,
            description: `Page ${page} of ${player.get<number>("pages")}. Modifiers: ${modifiers}`,
            url: track.uri,
            author: {
                name: `Current queue: Showing #${listStart + 1} to #${listEnd + 1} of ${player.queue.length} items in queue.`,
                url: "https://tinyurl.com/boomermusic",
                icon_url: "https://i.imgur.com/dpVBIer.png"
            },
            footer: {
                text: "<> for page +/-"
            },
            fields: []
        }

        if (TrackUtils.isTrack(track)) {
            this.data.thumbnail = {
                url: `https://i.ytimg.com/vi/${track.identifier}/mqdefault.jpg`
            }

        } else {
            this.data.thumbnail = {
                url: "https://i.imgur.com/hpjK2ym.png"
            }
        }

        for (var i = listStart; i < (player.queue.length == 1 ? listEnd : listEnd + 1); i++) {
            let track = player.queue.at(i) as Track | UnresolvedTrack

            let playTime = timeFormat(track.duration!, {leading: true}) as String

            this.data.fields!.push({
                name: truncate(`${i + 1}. *${track.title}*`, config.music.listCharLength),
                value: `${playTime}`,
                inline: false
            })
        }
    }

    toJSON() {
        return new EmbedBuilder(this.data).toJSON()
    }
}