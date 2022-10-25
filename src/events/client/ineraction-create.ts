import { ExtendedClient, ClientEvent } from "../../util/structures";

export const event: ClientEvent = {
    name: "interactionCreate",
    async listen(client: ExtendedClient) {

        // monitor for slash commands and handle them seperately
        client.on("interactionCreate", async interaction => {

            if (interaction.isCommand()) {
                const command = client.commands.get(interaction.commandName);

                if (!command) return;

                try {
                    await command.execute(interaction, client);
                } catch (error) {
                    console.error(error);
                    const interactionState = [
                        (interaction.deferred ? "DEFERRED" : ""),
                        (interaction.replied ? "REPLIED" : "")
                    ].filter(Boolean).join("_")

                    switch (interactionState) {
                        case "DEFERRED":
                            await interaction.editReply({ content: `${error}` });
                            break;

                        case "REPLIED":
                            await interaction.editReply({ content: `${error}` });
                            break;

                        case "DEFERRED_REPLIED":
                            await interaction.followUp({ content: `${error}`, ephemeral: true });
                            break;

                        default:
                            await interaction.reply({ content: `${error}`, ephemeral: true });
                            break;
                    }

                    throw new Error("Command errored. Shutting down. This could be intentional, but check bot output just in case.")
                }
            }
        })
    }
}