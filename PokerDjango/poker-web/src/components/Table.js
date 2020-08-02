import React, {useState, useEffect} from 'react';
import '../styles/table.css';
import '../styles/player.css';
import Player from './Player.js'
import Button from 'react-bootstrap/Button';
import Card from './Card.js';
import { Container, Row, Col } from 'react-bootstrap';
import { Layout } from './Layout.js';
import Cookies from 'js-cookie';

function loadGame(callback){
    const xhr = new XMLHttpRequest()
    const method = 'GET'
    const url = "http://localhost:8000/api/game/"
    const responseType = "json"
    xhr.responseType = responseType
    xhr.open(method, url)
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
    const [pot, setPot] = useState("0")
    const [loaded, setLoaded] = useState(false)
    const [placeholder, setPlaceholder] = useState("Loading")
    
    useEffect(() => {
        const myCallback = (response, status) => {
            if(status === 200){
                const data = response.slice(response.length-1)[0]
                console.log(data["total_pot"])
                setPot(data["total_pot"])
            }
        }
        loadGame(myCallback)
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
                    <div className="board">
                        <Card value={'A'} suit={'s'}/>
                        <Card value={'K'} suit={'s'}/>
                        <Card value={'5'} suit={'d'}/>
                        <Card value={'7'} suit={'c'}/>
                        <Card value={'J'} suit={'h'}/>
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