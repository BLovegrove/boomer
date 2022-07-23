import { Client, ClientOptions, Collection } from "discord.js";
import { Manager } from "erela.js";
import { Command } from "./command";
import config from "../../config.json"
import { CommandHelper } from "../helpers/commands";
import path from "path"

// export type ExtendedClient = Client & { manager: Manager }

export class Boomer extends Client {

    commands: Collection<String, Command>
    manager: Manager

    constructor(options: ClientOptions, manager: Manager) {
        super(options);
        
        this.manager = manager
        
        // grab the command files and generate a collection from them
        this.commands = CommandHelper.load(path.join(__dirname, "../../commands"))
        // register the commands with the discord API to display them on the server
        CommandHelper.register(this.commands)
    }

    connect() {
        return super.login(config.bot.token);
    };
};