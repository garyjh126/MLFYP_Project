import React, {useState, useEffect} from 'react';
import '../styles/table.css';
import '../styles/player.css';
import Player from './Player.js'
import Button from 'react-bootstrap/Button';
import Card from './Card.js';
import { Container, Row, Col } from 'react-bootstrap';
import { Layout } from './Layout.js';
import Cookies from 'js-cookie';

function loadDetails(callback, url){
    const xhr = new XMLHttpRequest()
    const method = 'GET'
    const responseType = "json"
    xhr.responseType = responseType
    xhr.open(method, url)
    xhr.setRequestHeader('Authorization', 'Token caf80ff750f4fce1d5f58b6f79a90cc0ef47614c')
    xhr.onload = function(){
        callback(xhr.response, xhr.status)
    }
    xhr.onerror = function(){
        callback({
            "message": "The request was an error"
        }, 400)
    }
    xhr.send()
}


function Table(props){
    const [pot, setPot] = useState("")
    const [loaded, setLoaded] = useState(false)
    const [communityCards, setCommunityCards] = useState([
        {id: 0, card_str: '9c', game: 0},
    ])
    const [playerGuest, setPlayerGuest] = useState([
        {
            "id": "",
            "name": "",
            "stack": "",
            "games": [],
            "cards": []
        }
    ])

    const [playerAI, setPlayerAI] = useState([
        {
            "id": "",
            "name": "",
            "stack": "",
            "games": [],
            "cards": []
        }
    ])

    
    
    useEffect(() => {
        const gamesCallback = (response, status) => {
            if(status === 200){
                const data = response.slice(response.length-1)[0]
                setPot(data["total_pot"])
            }
        }
        loadDetails(gamesCallback, "http://localhost:8000/api/games/")

        const playersCallback = (response, status) => {
            if(status === 200){
                const playerGuest = response.slice(response.length-2)[0]
                const playerAI = response.slice(response.length-1)[0]
                console.log("playerGuest", playerGuest)
                console.log("playerAI", playerAI)
                setPlayerGuest(playerGuest)
                setPlayerAI(playerAI)
            }
        }
        loadDetails(playersCallback, "http://localhost:8000/api/players/")

        
        // This is to be called after preflop
        const communityCardsCallback = (response, status) => {
            if(status === 200){
                console.log("communityCardsCallback", response)
                setCommunityCards(response)
            }

        }
        
        loadDetails(communityCardsCallback, `http://localhost:8000/api/community_cards/`)


        const playerGuestCardsCallback = (response, status) => {
            if(status === 200){
                console.log("playerGuestCardsCallback", response)
                setPlayerGuest(...playerGuest, response)
            }

        }
        console.log("PLAYER cards ", playerGuest)
        console.log("PLAYER cards URL", `http://localhost:8000/api/players/${playerGuest}/display_player_cards/`)
        loadDetails(playerGuestCardsCallback, `http://localhost:8000/api/players/${playerGuest.id}/display_player_cards/`)

        const playerAICardsCallback = (response, status) => {
            if(status === 200){
                console.log("playerAICardsCallback", response)
                setPlayerAI(...playerAI, response)
            }

        }
        loadDetails(playerAICardsCallback, `http://localhost:8000/api/players/${playerAI.id}/display_player_cards/`)
        
    }, [])

    return (
        <div>
            <Layout>
                <Row>
                    <Col>
                        <div className="heading">
                            <h1>Texas Hold'Em</h1>
                        </div>
                    </Col>
                </Row>
                <div className="table">
                    <div id="board" className="board">
                        {communityCards.map((card, index) => (
                            <Card 
                                key={index}
                                index={index}
                                value={card.card_str.substring(0,1)}
                                suit={card.card_str.substring(1,2)}
                            />
                        ))}
                    </div>
                    <Row>
                        <Col>
                            <h1>Pot: ${pot}</h1>
                        </Col>
                    </Row>
                    
                    <Row>   
                        <Col>   
                            <Player is_ai={false} />
                        </Col>  
                        <Col>   
                            <Player is_ai={true} />
                        </Col>  
                    </Row>  

                    <Row>
                        <div className="mx-auto mt-3">
                            <Button variant="success" size="lg" block>Check/Call</Button>
                            <Button variant="danger" size="lg" block>Bet/Raise</Button>
                            <Button variant="light" size="lg" block>Fold</Button>
                        </div>
                    </Row>
                </div>
            </Layout>
        </div>

    )

}

export default Table;