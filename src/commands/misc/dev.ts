import { SlashCommandBuilder } from "@discordjs/builders";
import { PermissionFlagsBits } from "discord-api-types/v10";
import { CommandInteraction } from "discord.js";
import { VoiceHelper } from "../../util/helpers";
import { Boomer, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("dev")
        .setDescription("Series of dev commands for boomer.")
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
        .addStringOption(option =>
            option
                .setName("subcommand")
                .setDescription("Runs a series of dev actions without cluttering the commands list")
                .setRequired(true)
                .addChoices(
                    {name: 'Kill bot', value: 'die'},
                    {name: 'Ping test', value: 'ping'},
                    {name: 'Log Search Example', value: 'searchex'},
                    {name: 'Log queue entries', value: 'logqueue'}
                )
        )
    ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        const subCommand = interaction.options.getString("subcommand", true)

        const VH = new VoiceHelper(client)
        const player = await VH.ensureVoice(interaction)
        if (!player) {
            return
        }

        await interaction.deferReply()

        switch (subCommand) {
            case "die":
                await interaction.editReply("My battery is low and it's getting dark :(")

                return

            case "ping":
                await interaction.editReply(`Pong! (${client.ws.ping}ms)`)

                return

            case "searchex":
                console.log("Text search result:");
                console.log(await player.search("Rick Astley"));

                console.log("YT Track result:")
                console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ"));

                console.log("YT Playlist result:");
                console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLCiNIjl_KpQhFwQA3G19w1nmhEOlZQsGF"))

                await interaction.editReply("Success.")
                await interaction.followUp({content: "Logged test results. Go check client log.", ephemeral: true})

                return
            
            case "logqueue":
                console.log(player.queue)

                await interaction.editReply("Success.")
                await interaction.followUp({content: "Logged queue. Go check client log", ephemeral: true})

                return
            
            default:
                await interaction.editReply("Dev command failed. Couldn't find a subcommand.")

                return
        }
    }
}