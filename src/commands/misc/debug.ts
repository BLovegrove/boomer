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
        .addSubcommand(subcommand => 
            subcommand
                .setName("die")
                .setDescription("Kills boomer and closes the bot client")
        )
        .addSubcommand(subcommand => 
            subcommand
                .setName("ping")
                .setDescription("Replies with Pong!")
        )
        .addSubcommand(subcommand =>
            subcommand
                .setName("logSearchExample")
                .setDescription("Logs 3 examples to client console showing search_result, track_loaded, & playlist_loaded objects")
        )
        .addSubcommand(subcommand =>
            subcommand
                .setName("logQueue")
                .setDescription("Logs the entire queue object to the client console")
        )
    ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        const subCommand = interaction.options.getSubcommand(true)

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

            case "logSearchExample":
                console.log("Text search result:");
                console.log(await player.search("Rick Astley"));

                console.log("YT Track result:")
                console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ"));

                console.log("YT Playlist result:");
                console.log(await player.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLCiNIjl_KpQhFwQA3G19w1nmhEOlZQsGF"))

                interaction.editReply("Success.")
                interaction.followUp({content: "Logged test results. Go check client log.", ephemeral: true})

                return
            
            case "logQueue":
                console.log(player.queue)

                interaction.editReply("Success.")
                interaction.followUp({content: "Logged queue. Go check client log", ephemeral: true})

                return
            
            default:
                interaction.editReply("Dev command failed. Couldn't find a subcommand.")

                return
        }
    }
}