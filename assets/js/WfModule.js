// UI for a single module within a workflow

import React from 'react'
import WfParameter from './WfParameter'
import TableView from './TableView'
import WfModuleContextMenu from './WfModuleContextMenu'
import { store, wfModuleStatusAction } from './workflow-reducer'
import { csrfToken } from './utils'
import * as Actions from './workflow-reducer'
import PropTypes from 'prop-types'

// Libraries to provide a collapsable table view
import { Collapse, Button, CardBlock, Card } from 'reactstrap';

// ---- StatusLight ----
// Ready, Busy, or Error
class StatusBar extends React.Component {
  render() {
    return <div className={this.props.status + '-bar'}></div>
  }
}

// ---- StatusLine ----
// Display error message, if any
class StatusLine extends React.Component {
  render() {
    if (this.props.status == 'error') {
      return <div className='wfModuleErrorMsg'>{this.props.error_msg}</div>
    } else if (this.props.status == 'busy') {
      return <div className='wfModuleErrorMsg'>Working...</div>
    } else {
      return false
    }
  }
}

// ---- WfModule ----

export default class WfModule extends React.Component {

  constructor(props) {
    super(props);
    this.initFields(props);
    this.click = this.click.bind(this);
    this.setParamText = this.setParamText.bind(this);
    this.getParamText = this.getParamText.bind(this);
    this.removeModule = this.removeModule.bind(this);
    this.state = {isOpen: false};           // componentDidMount will trigger first load
    this.toggle = this.toggle.bind(this);
  }

  // our props are annoying (we use data- because Sortable puts all these props om the DOM object)
  // so save them into this
  initFields(props) {
    this.wf_module = props['data-wfmodule'];
    this.module = this.wf_module.module_version.module;
    this.params = this.wf_module.parameter_vals;
    this.revision = props['data-revision'];
  }

  // alas, the drawback of the convienence of initFields is we need to call it whenever props change
  componentWillReceiveProps(newProps) {
    this.initFields(newProps)
  }

  // We become the selected module on any click
  click(e) {
    Actions.store.dispatch(Actions.changeSelectedWfModuleAction(this.wf_module.id));
  }

  // These functions allow parameters to access each others value (text params only)
  // Used e.g. for custom UI elements to save/restore their state from hidden parameters
  // Suppresses reassignment of the same text, which can be important to avoid endless notification loops
  setParamText(id_name, text) {
    var p = this.params.find( p => p.parameter_spec.id_name == id_name );
    if (p && text != p.string) {
      this.props['data-changeParam'](p.id, { value: text })
    }
  }

  getParamText(id_name) {
    //console.log("getParamText " + id_name)
    var p = this.params.find( p => p.parameter_spec.id_name == id_name );
    if (p) {
      return p.value;
    }
  }

  removeModule(e) {
    this.props['data-removeModule'](this.wf_module.id);
  }

  toggle() {
    this.setState({isOpen: !this.state.isOpen});
  }

  render() {

    // Each parameter gets a WfParameter
    var paramdivs = this.params.map((ps, i) => {
        return <WfParameter
          key={i}
          p={ps}
          changeParam={this.props['data-changeParam']}
          wf_module_id={this.wf_module.id}
          revision={this.revision}
          getParamText={this.getParamText}
          setParamText={this.setParamText} />
      });

    var cardClass = this.props['data-selected'] ?
      'card border-selected-module':
      'card ';

    var inside = undefined;
    if (this.state.isOpen)
      inside = <div>{paramdivs}</div>;

    // Putting it all together: name, status, parameters, output
    return (
      <div className='container' {...this.props} onClick={this.click}>
        <div className={cardClass}>
          <div className='card-block p-1 module-card-wrapper'>
            {/* --- Everything but the status bar, on the left of card --- */}
            <div className='module-card-info'>
              <div 
                className='d-flex justify-content-between align-items-center mb-2 '
                onClick={this.toggle}
              >
                <h4 className='text-center mb-0'>{this.module.name}</h4>
                <WfModuleContextMenu 
                  removeModule={ () => this.removeModule() }
                  stopProp={(e) => e.stopPropagation()}
                  id={this.wf_module.id}
                  className="menu-test-class"
                />
              </div>
              <StatusLine status={this.wf_module.status} error_msg={this.wf_module.error_msg} />
              {/* --- Module details, will expand / collapse --- */}
              <Collapse className='mt-1 pl-2 pr-2' isOpen={this.state.isOpen} >
                {inside}
              </Collapse>  
            </div>
            {/* --- Color indicator of module status, on the right of card --- */}
            <div className='module-status-bar'>  
              <StatusBar status={this.wf_module.status}/>
            </div>
          </div>

        </div>
      </div>
    ); 
  } 
}


WfModule.propTypes = {
  'data-wfmodule':      PropTypes.object,
  'data-revison':       PropTypes.number,
  'data-selected':      PropTypes.bool,
  'data-changeParam':   PropTypes.func,
  'data-removeModule':  PropTypes.func
};
