package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"

	"github.com/gin-gonic/gin"
)

const (
	CLIENT_ID     = ""
	CLIENT_SECRET = ""
	REDIRECT_URI  = ""
	SCOPE         = ""
	STATE         = "NICE"
)

func auth(c *gin.Context) {
	params := url.Values{
		"client_id":     {CLIENT_ID},
		"response_type": {"code"},
		"redirect_uri":  {REDIRECT_URI},
		"scope":         {SCOPE},
		"state":         {STATE},
	}

	queryString := params.Encode()

	fmt.Println(queryString)

	c.Redirect(http.StatusFound, "https://accounts.spotify.com/authorize?"+queryString)
}

func root(c *gin.Context) {
	params := c.Request.URL.Query()

	if params["state"][0] != STATE {
		c.String(200, "Bad state value!")
		return
	}

	accessToken := getAcessToken(params["code"][0])

	if accessToken == "" {
		c.String(200, "Failed getting access token!")
		return
	}

	req, err := http.NewRequest("GET", "https://api.spotify.com/v1/me", nil)

	if err != nil {
		c.String(200, "Failed creating request object")
		return
	}

	req.Header.Add("Authorization", "Bearer "+accessToken)

	resp, err := http.DefaultClient.Do(req)

	if err != nil || resp.StatusCode != 200 {
		c.String(200, "Failed requesting API")
		return
	}

	body, err := io.ReadAll(resp.Body)

	if err != nil {
		c.String(200, "Failed reading body")
		return
	}

	var data map[string]interface{}
	json.Unmarshal(body, &data)

	c.String(200, data["id"].(string))
}

func getAcessToken(code string) string {
	payload := url.Values{
		"code":         {code},
		"grant_type":   {"authorization_code"},
		"redirect_uri": {REDIRECT_URI},
	}

	req, err := http.NewRequest("POST", "https://accounts.spotify.com/api/token", strings.NewReader(payload.Encode()))

	if err != nil {
		fmt.Println("Failed creating request")
		return ""
	}

	auth_header := base64.StdEncoding.EncodeToString([]byte(CLIENT_ID + ":" + CLIENT_SECRET))

	req.Header.Add("Authorization", "Basic "+auth_header)
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	resp, err := http.DefaultClient.Do(req)

	if err != nil {
		fmt.Println("Failed requesting access token")
		return ""
	}

	body, err := io.ReadAll(resp.Body)

	if err != nil {
		fmt.Println("Failed reading body")
		return ""
	}

	var data map[string]interface{}
	json.Unmarshal(body, &data)

	fmt.Println("Got access TOKEN")
	return data["access_token"].(string)
}

func main() {
	r := gin.Default()
	r.GET("/auth", auth)
	r.GET("/main", root)

	r.Run("localhost:5000")
}
