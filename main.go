package brobot

import (
	"github.com/bwmarrin/discordgo"
	"os"
)

func main() {
	// Create a new Discord session using the provided bot token.
	bot, err := discordgo.New("Bot " + os.Getenv("DISCORD_TOKEN"))
	if err != nil {
		println("error creating Discord session,", err)
		return
	}
	defer bot.Close()

}