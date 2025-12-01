use multiversx_sc_scenario::*;

fn world() -> ScenarioWorld {
    let mut blockchain = ScenarioWorld::new();

    // register the compiled wasm artifact and the contract builder from the contract crate
    const CODE_PATH: &str = "file:wasm/target/wasm32-unknown-unknown/release/trail_control_wasm.wasm";
    blockchain.register_contract(CODE_PATH, trail_control::ContractBuilder);

    blockchain
}

#[test]
fn deploy_and_mark_scenario() {
    let world = world();
    world.run("scenarios/deploy_and_mark.scen.json");
}
