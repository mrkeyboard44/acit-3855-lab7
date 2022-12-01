import React, { useEffect, useState } from 'react'
import '../App.css';
import { Stack } from "@mui/material";

export default function EndpointHealth(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [health, setHealth] = useState(null);
    const [error, setError] = useState(null);
	// const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
    const getHealth = () => {
        fetch(`http://acit-3855-matt-kafka.westus3.cloudapp.azure.com/health/check`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Results")
                setHealth(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
	useEffect(() => {
		const interval = setInterval(() => getHealth(), 5000); // Update every 4 seconds
		return() => clearInterval(interval);
    }, [getHealth]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        const color = (status) => {
            if (status == 'Running') {
                return 'statusGreen'
            } else {
                return 'statusRed'
            }
        }

        const [date, time_with_sec] = health['last_update'].split('T')
        const [time, _ ] = time_with_sec.split('.')
        let last_update = String(date) + ' ' + String(time)

        return (

            <div className='Health'>
                <Stack direction={'row'} justifyContent={'space-evenly'} spacing={2}>
                    <Stack>
                        <h4>Reciever Status:</h4>
                        <p className={color(health['receiver'])}>{health['receiver']}</p>

                    </Stack>
                    <Stack>
                        <h4>Storage Status:</h4>
                        <p className={color(health['storage'])}>{health['storage']}</p>

                    </Stack>
                    <Stack>
                        <h4>Processing Status:</h4>
                        <p className={color(health['processing'])}>{health['processing']}</p>
                        
                    </Stack>
                    <Stack>
                        <h4>Audit Log Status:</h4>
                        <p className={color(health['audit_log'])}>{health['audit_log']}</p>
                        
                    </Stack>
                </Stack>

						
                <h3>Last Updated: {last_update}</h3>
            </div>
        )
    }
}
