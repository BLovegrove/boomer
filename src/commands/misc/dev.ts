import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { CommandHelper, VoiceHelper } from "../../util/helpers";
import { ExtendedClient, Command } from "../../util/structures";
import { PermissionFlagsBits } from "discord-api-types/v10";
import config from "../../config.json"

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("dev")
        .setDescription("Series of dev commands for boomer.")
        .setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild)
        .addStringOption(option =>
            option
                .setName("subcommand")
                .setDescription("Runs a series of dev actions without cluttering the commands list")
                .setRequired(true)
                .addChoices(
                    {name: 'Kill bot', value: 'die'},
                    {name: 'Ping test', value: 'ping'},
                    {name: 'Log Search Example', value: 'searchex'},
                    {name: 'Log queue entries', value: 'logqueue'},
                    {name: 'Log player state', value: 'logplayer'}
                )
        )
    ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const subCommand = interaction.options.getString("subcommand", true)

        const VH = new VoiceHelper(client)

        await interaction.deferReply({ephemeral: true})

        switch (subCommand) {
            case "die":
                if (client.playerExists) {
                    await VH.disconnect(VoiceHelper.fetchPlayer(client))
                }
                await interaction.editReply(`${config.bot.name} now rebooting. Wait until they're online again before ruing more commands.`)
                client.destroy()
                CommandHelper.deRegister()
                throw new Error("My battery is low and it's getting dark :(")

            case "ping":
                await interaction.editReply(`Pong! (${client.ws.ping}ms)`)

                return

            case "searchex":
                var player = await VH.ensureVoice(interaction)
                if (!player) {
                    return
                }

                console.log("Text search result:");
                console.log(await player.search("Rick Astley"));

                console.log("YT Track result:")
                console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ"));

                console.log("YT Playlist result:");
                console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLCiNIjl_KpQhFwQA3G19w1nmhEOlZQsGF"))

                await interaction.editReply({content: "Logged test results. Go check client log."})

                return
            
            case "logqueue":
                var player = await VH.ensureVoice(interaction)
                if (!player) {
                    return
                }

                console.log(player.queue)

                await interaction.editReply({content: "Logged queue. Go check client log"})

                return
            
            case "logplayer":
                var player = await VH.ensureVoice(interaction)
                if (!player) {
                    return
                }
                
                console.log(player)

                await interaction.editReply({content: "Logged player object. Go check the client log"})
                
                return
            
            default:
                await interaction.editReply("Dev command failed. Couldn't find a subcommand.")

                return
        }
    }
}