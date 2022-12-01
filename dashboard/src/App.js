import icon from './icon.webp';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'
import EndpointHealth from './components/HealthCheck';


function App() {

    const endpoints = ["exerciseData", "userParameters"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

   

    return (
        <div className="App">
            <img src={icon} className="App-logo" alt="logo" height="150px" width="150px"/>
            <div>
                <AppStats/>
                <h1>Audit Endpoints</h1>
                {rendered_endpoints}
                <h1>Health Checks</h1>
                <EndpointHealth/>
            </div>
        </div>
    );

}


    
export default App;
