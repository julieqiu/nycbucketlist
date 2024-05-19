package main

import (
	// import standard libraries
	// Import the GenerativeAI package for Go
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

const directory = "/Users/julieqiu/Downloads/tiktok"

func main() {
	ctx := context.Background()
	if err := run(ctx, directory); err != nil {
		log.Fatal(err)
	}
}

func run(ctx context.Context, dir string) error {
	files, err := os.ReadDir(dir)
	if err != nil {
		return err
	}

	for _, f := range files {
		if err := makeGeminiRequest(ctx, filepath.Join(dir, f.Name())); err != nil {
			return err
		}
	}

	/*
		g := new(errgroup.Group)
		for _, f := range files {
			f := f
			g.Go(func() error {
				return makeGeminiRequest(ctx, filepath.Join(dir, f.Name()))
			})
		}
		// Wait for all HTTP fetches to complete.
		if err := g.Wait(); err != nil {
			return err
		}
	*/
	return nil
}

func makeGeminiRequest(ctx context.Context, filename string) error {
	// Access your API key as an environment variable
	client, err := genai.NewClient(ctx, option.WithAPIKey(os.Getenv("GOOGLE_API_KEY")))
	if err != nil {
		return err
	}
	defer client.Close()

	// Use client.UploadFile to upload a file to the service.
	// Pass it an io.Reader.
	f, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer f.Close()

	// Optionally set a display name.
	opts := &genai.UploadFileOptions{DisplayName: "Sample"}
	// Let the API generate a unique `name` for the file by passing an empty string.
	// If you specify a `name`, then it has to be globally unique.
	file, err := client.UploadFile(ctx, "", f, opts)
	if err != nil {
		return fmt.Errorf("client.UploadFile: %v", err)
	}

	/*
		for {
			resp, err := client.GetFile(ctx, file.Name)
			if err != nil {
				return err
			}
			if resp.State != genai.FileStateProcessing {
				break
			}
		}
	*/
	time.Sleep(15 * time.Second)

	// View the response.
	fmt.Printf("Uploaded file %s as: %q\n", file.DisplayName, file.URI)

	// Initialize the generative model with a model that supports multimodal input.
	model := client.GenerativeModel("gemini-1.5-pro-latest")

	// Create a prompt using text and the URI reference for the uploaded file.
	prompt := []genai.Part{
		genai.FileData{URI: file.URI},
		genai.Text("You are creating a NYC bucket list and want a list of places to visit. Tell me the places recommended in this video."),
	}

	// Generate content using the prompt.
	resp, err := model.GenerateContent(ctx, prompt...)
	if err != nil {
		return fmt.Errorf("model.GenerateContent: %v", err)
	}

	for _, c := range resp.Candidates {
		fmt.Println(*c.Content)
		fmt.Println(strings.Repeat("-", 80))
	}
	return nil
}
