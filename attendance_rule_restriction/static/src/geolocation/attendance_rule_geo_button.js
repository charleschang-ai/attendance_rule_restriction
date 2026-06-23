/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { rpc } from "@web/core/network/rpc";

export class GeoDetectButton extends Component {
    static template = "attendance_rule_restriction.GeoDetectButton";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.notification = useService("notification");
    }

    async onClick() {
        if (!navigator.geolocation) {
            this.notification.add("Your browser does not support geolocation.", {
                type: "danger",
            });
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                await rpc("/web/dataset/call_kw", {
                    model: "attendance.rule",
                    method: "action_add_current_geo",
                    args: [[this.props.record.resId], latitude, longitude],
                    kwargs: {},
                });
                this.notification.add(
                    `Location (${latitude.toFixed(6)}, ${longitude.toFixed(6)}) added.`,
                    { type: "success" }
                );
                await this.props.record.load();
                this.props.record.model.notify();
            },
            () => {
                this.notification.add(
                    "Unable to get location. Please allow location access in your browser.",
                    { type: "danger" }
                );
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }
}

// extractProps 只處理自定義屬性，record 由框架自動傳入
export const geoDetectButton = {
    component: GeoDetectButton,
    extractProps: (widgetInfo, dynamicInfo) => ({}),
};

registry.category("view_widgets").add("geo_detect_button", geoDetectButton);