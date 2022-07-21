import { SlashCommandBuilder } from "discord.js";
import { Command } from "../../types"

// export var must always be 'command' - see 'add command module files to collection' in index.ts
// : Command type adds strong typing for interaction and client args! Thank god for typescript
export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("default")
        .setDescription("default"),
    async execute(interaction, client) {
        // any code you need to execute you can run here.
        return interaction.reply("Hi :)")
    }
}