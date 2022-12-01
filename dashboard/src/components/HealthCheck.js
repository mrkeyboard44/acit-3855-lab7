import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointHealth(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null);
	// const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store
    const rand_val = 1
    const getHealth = () => {
        setIndex(rand_val)
        fetch(`http://acit-3855-matt-kafka.westus3.cloudapp.azure.com/health/check`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Results")
                setLog(result);
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
        
        return (
            <div className='Health'>
                <h1>Health Check</h1>
                <p id='Health'>{JSON.stringify(log).replaceAll('{','{\t').replaceAll(',', ',\n\t').replaceAll('}', '\t}')}</p>
            </div>
        )
    }
}
