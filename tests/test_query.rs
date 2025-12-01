use multiversx_sc_scenario::*;

fn world() -> ScenarioWorld {
    let mut blockchain = ScenarioWorld::new();
    blockchain.register_contract("mxsc:output/trail_control.mxsc.json", trail_control::ContractBuilder);
    blockchain
}

#[test]
fn test_mark_and_query() {
    let mut world = world();
    let trail_control_code = world.code_expression("mxsc:output/trail_control.mxsc.json");

    let owner_address = "address:owner";
    let user1_address = "address:user1";
    
    world
        .start_trace()
        .account(owner_address)
        .nonce(1)
        .account(user1_address)
        .nonce(1);

    let trail_control_address = world
        .tx()
        .from(owner_address)
        .typed(trail_control_proxy::TrailControlProxy)
        .init()
        .code(trail_control_code)
        .new_address(owner_address)
        .returns(ReturnsNewAddress)
        .run();

    // Mark checkpoint 1 for user1
    world
        .tx()
        .from(user1_address)
        .to(&trail_control_address)
        .typed(trail_control_proxy::TrailControlProxy)
        .mark_checkpoint(1u32)
        .run();

    // Mark checkpoint 2 for user1
    world
        .tx()
        .from(user1_address)
        .to(&trail_control_address)
        .typed(trail_control_proxy::TrailControlProxy)
        .mark_checkpoint(2u32)
        .run();

    // Query checkpoints for user1
    let result = world
        .query()
        .to(&trail_control_address)
        .typed(trail_control_proxy::TrailControlProxy)
        .get_checkpoints_for(user1_address)
        .returns(ReturnsResult)
        .run();

    println!("Query result: {:?}", result);
    assert!(result.len() > 0, "Should have at least one checkpoint");

    world.write_scenario_trace("trace_query_test.scen.json");
}
