import React, { useEffect, useState } from 'react'
import '../App.css';
import { Stack } from "@mui/material";


export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit-3855-matt-kafka.westus3.cloudapp.azure.com:8100/events/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })  
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 5000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        // console.log(stats['last_updated'])
        // const [year, month, day_time] = stats['last_updated'].split('-')
        // console.log('year, month, day', year, month, day_time)
        const [date, time_with_sec] = stats['last_updated'].split('T')
        const [time, _ ] = time_with_sec.split('.')
        let last_updated = String(date) + ' ' + String(time)
        return (
            <div>
                <h1>Latest Stats</h1>
                <Stack direction={'row'} justifyContent={'space-evenly'} spacing={2}>
                    <Stack>
                        <h4>Recording ID</h4>
                        <p>{stats['recording_id']}</p>

                    </Stack>
                    <Stack>
                        <h4>Total Recordings</h4>
                        <p>{stats['total_recordings']}</p>

                    </Stack>
                    <Stack>
                        <h4>Total Reps</h4>
                        <p>{stats['total_reps']}</p>
                        
                    </Stack>
                    <Stack>
                        <h4>Max BPM</h4>
                        <p>{stats['max_heart_rate']}</p>
                        
                    </Stack>
                    <Stack>
                        <h4>Min BPM</h4>
                        <p>{stats['min_heart_rate']}</p>
                        
                    </Stack>
                    <Stack>
                        <h4>Calories Burned</h4>
                        <p>{stats['calories_burned']}</p>
                    </Stack>
                </Stack>

						
                <h3>Last Updated: {last_updated}</h3>

            </div>
        )
    }
}


// <tr>
// 							<td colspan="2">Recording ID: {stats['recording_id']}</td>
						
// 							<td colspan="2">Total Recordings: {stats['total_recordings']}</td>
						
// 							<td colspan="2">Total Reps: {stats['total_reps']}</td>
						
// 							<td colspan="2">Max BPM: {stats['max_heart_rate']}</td>
						
// 							<td colspan="2">Min BPM: {stats['min_heart_rate']}</td>
						
// 							<td colspan="2">Calories Burned: {stats['calories_burned']}</td>
// 						</tr>