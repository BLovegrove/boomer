import { Client, ClientOptions, Collection } from "discord.js";
import { Manager } from "erela.js";
import { Command } from "./command";
import config from "../../config.json"
import { CommandHelper } from "../helpers/command";
import path from "path"

// export type ExtendedClient = Client & { manager: Manager }

export class Boomer extends Client {

    commands: Collection<String, Command>
    manager: Manager
    playerExists: boolean

    constructor(options: ClientOptions, manager: Manager) {
        super(options);
        
        this.manager = manager
        this.playerExists = manager.players.values.length != 0 ? true : false
        
        // grab the command files and generate a collection from them
        this.commands = CommandHelper.load(path.join(__dirname, "../../commands"))
        // register the commands with the discord API to display them on the server
        CommandHelper.register(this.commands)
    }

    connect() {
        return super.login(config.bot.token);
    };
};